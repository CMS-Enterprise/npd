The files in this folder were automatically generated from a combination of Pydantic FHIR models in the backend/ project to generate schema .json files and the use of `json2ts` in the frontend/ project to generate `.ts` Typescript interface definitions.

From the project root:

```sh
# create a JSON schema for the given FHIR resource type
docker compose run --rm django-web \
    python manage.py exportschema \
    --model Organization --schema \
    > frontend/src/@types/fhir/organization_schema.json

# use the schema to generate a Typescript type definition
docker compose run --rm web \
    npx json2ts src/@types/fhir/organization_schema.json \
    > frontend/src/@types/fhir/Organization.ts
```

As a repeatable command, you could add this to your local `scratch/` folder and run it:

```sh
#!/usr/bin/env bash

model=${1}
model_lower="$(echo $model | tr '[:upper:]' '[:lower:]')"

if [ -z "$model" ] || [ -z "$model_lower" ]; then
  echo "ignoring unset model:${model} or model_lower:${model_lower}"
  exit 1
fi

echo "exporting ${model} (${model_lower}) to Typescript"

docker compose run --rm django-web \
    python manage.py exportschema \
    --model $model --schema \
    > frontend/src/@types/fhir/${model_lower}_schema.json

docker compose run --rm web \
    npx json2ts src/@types/fhir/${model_lower}_schema.json \
    > frontend/src/@types/fhir/${model}.ts
```

## Finding the right model to export

In the FHIR API we're serving from backend/npdfhir, the type of the API output is determined by the Pydantic model used by the serializer provided to the view.

For example, in the case of `/fhir/Organization/{id}`:

- the view is `npdfhir.views.FHIROrganizationViewSet`
- the `retrieve` method on the view shows us the serializer is `npdfhir.serializers.OrganizationSerializer`
- the `to_representation` method on the serializer shows us the base model is `fhir.resources.R4B.organization.Organization`

Conclusion, we need to convert `fhir.resources.R4B.organization.Organization` to a Typescript interface in order to correctly model the FHIR API in the frontend application.

## Additional type exports

The `fhir.resources` project defines top level Pydantic models, but does not set the fields to the corresponding Pydantic model types. This causes the `.model_json_schema()` method to export JSON schemas with unhelpful type definitions.

For example, `frontend/src/@types/fhir/practitioner_schema.json:346-360`:

```json
"name": {
  "anyOf": [
    {
      "items": {},
      "type": "array"
    },
    {
      "type": "null"
    }
  ],
  "default": null,
  "element_property": true,
  "summary_element_property": true,
  "title": "The name(s) associated with the practitioner"
},
```

In Typescript, that's translated to `frontend/src/@types/fhir/Practitioner.ts:58-58`:

```typescript
export type TheNameSAssociatedWithThePractitioner = unknown[] | null
```

Too many `unknown`s.

To get at the actual underlying type in this exapmple, we have to open the Practitioner model to see the `name` field's implementation, `backend/.venv/lib/python3.13/site-packages/fhir/resources/R4B/practitioner.py:117-126`:

```python
name: typing.List[fhirtypes.HumanNameType] | None = Field(  # type: ignore
    default=None,
    alias="name",
    title="The name(s) associated with the practitioner",
    description=None,
    json_schema_extra={
        "element_property": True,
        "summary_element_property": True,
    },
)
```

And trace that to the `fhir.resources.fhirtypes.HumanNameType` implementation, `backend/.venv/lib/python3.13/site-packages/fhir/resources/R4B/fhirtypes.py:1476-1478`:

```python
HumanNameType = create_fhir_type(
    "HumanNameType", "fhir.resources.R4B.humanname.HumanName"
)
```

Which shows us that the underlying Pydantic model which will be exposed at `provider.name` is `fhir.resources.R4B.humanname.HumanName`.

That is enough information to run the JSON Schema --> Typescript interface flow for `HumanName` models.

```sh
docker compose run --rm django-web \
    python manage.py exportschema \
    --model HumanName --schema > frontend/src/@types/fhir/humanname_schema.json

docker compose run --rm web \
    npx json2ts src/@types/fhir/humanname_schema.json
```

Using the additional types correctly in API response handling is demonstrated in the organizations and providers API support files. For example, `frontend/src/state/requests/practitioners.ts`:

```typescript
import type { HumanName } from "../../@types/fhir/HumanName"
import type { Identifier } from "../../@types/fhir/Identifier"
import type { Practitioner as FhirPractitioner } from "../../@types/fhir/Practitioner"

export interface Practitioner extends FhirPractitioner {
  name?: HumanName[] | null
  identifier?: Identifier[] | null
}

// api queries and selector functions
```
