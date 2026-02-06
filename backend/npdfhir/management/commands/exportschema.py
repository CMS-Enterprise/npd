import base64
import importlib
import json
import random
from typing import Callable

from django.core.management.base import BaseCommand, CommandError
from django.db import models
from django.test import Client
from django.urls import reverse

# from fhir.resources.R4B import organization, practitioner
from pydantic import BaseModel

from npdfhir.models import Organization, Provider


class Command(BaseCommand):
    help = "Export a JSON schema, example JSON record, or both for a given FHIR entity"

    def add_arguments(self, parser):
        parser.add_argument(
            "--model",
            help="name of FHIR entity to export (Practitioner, Organization, etc)",
            default="Practitioner",
        )
        parser.add_argument(
            "--schema",
            help="only export the model_json_schema",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "--record",
            help="only export the an example record JSON dump",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "--username",
            help="username of a local NPD user (required if authentication is required)",
            default="developer@cms.hhs.gov",
        )
        parser.add_argument(
            "--password",
            help="password of a local NPD user (required if authentication is required)",
            default="password123",
        )

    def prepare_authentication_header(self, options: dict):
        username = options["username"]
        password = options["password"]
        payload_bytes = f"{username}:{password}".encode("utf-8")
        return f"Basic {base64.b64encode(payload_bytes).decode('utf-8')}"

    def load_fhir_model(self, model_name: str):
        module = importlib.import_module(f".R4B.{model_name.lower()}", "fhir.resources")
        return getattr(module, model_name)

    def get_record_and_schema(
        self,
        model_class: models.Model | None,
        api_class: BaseModel | str,
        route: str | None,
        options: dict,
        id_selector: Callable[[models.Model], str] | None,
    ) -> tuple[str, str]:
        schema = {}
        json_record = {}

        if isinstance(api_class, str):
            api_class = self.load_fhir_model(api_class)

        if not options["record"]:
            schema = api_class.model_json_schema()

        if not options["schema"]:
            client = Client()
            records = model_class.objects.all()[:10]
            example = random.choice(records)

            record_id = id_selector(example) if id_selector else example.id

            url = reverse(route, args=[record_id])
            resp = client.get(url, HTTP_AUTHORIZATION=self.prepare_authentication_header(options))
            json_record = json.loads(resp.content)

        return json_record, schema

    def handle(self, *args, **options):
        if str(options["model"]).lower().startswith("prac"):
            model_type = "Practitioner"
            json_record, schema = self.get_record_and_schema(
                Provider,
                model_type,
                "fhir-practitioner-detail",
                options,
                lambda record: record.individual.id,
            )
        elif str(options["model"]).lower().startswith("org"):
            model_type = "Organization"
            json_record, schema = self.get_record_and_schema(
                Organization,
                model_type,
                "fhir-organization-detail",
                options,
                lambda record: record.id,
            )
        else:
            model_type = options["model"]
            try:
                json_record, schema = self.get_record_and_schema(
                    None, model_type, None, {**options, "schema": True}, None
                )
            except Exception as ex:
                raise CommandError(f"unable to generate schema for {model_type}") from ex

        if options["schema"]:
            self.stdout.write(json.dumps(schema, indent=2))
        elif options["record"]:
            self.stdout.write(json.dumps(json_record, indent=2))
        else:
            self.stdout.write(
                f'Given this OpenAPI JSON schema document and an example JSON record, please generate a Typescript interface for "{model_type}" records.\n\n'
                f"<openapi-schema>\n{json.dumps(schema, indent=2)}\n</openapi-schema>\n\n"
                f"<json-record>\n{json.dumps(json_record, indent=2)}\n</json-record>\n\n"
            )
