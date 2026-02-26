import developers from "./developers.json"
import errors from "./errors.json"
import footer from "./footer.json"
import header from "./header.json"
import landing from "./landing.json"
import organizations from "./organizations.json"
import practitioners from "./practitioners.json"
import search from "./search.json"

/*
 * NOTE: (@abachman-dsac) a word about i18n usage in react components and the
 * names of keys
 *
 * Keys definied here use the root-level key shown below plus whatever hierarchy
 * is defined in the corresponding JSON file.
 *
 * For example, given header.json:
 *
 *   { "section": { "title": "Blah Section" } }
 *
 * The TFunction would reference that value with:
 *
 *   t('header.section.title')
 *
 * due to the use of `header` in the `translations` object here, and the direct
 * handing of the exported `translations` object to the i18n configuration.
 *
 * The use of "translations" as the `defaultNS` value in i18n.ts necessitates its
 * use here.
 */
export const translations = {
  developers,
  errors,
  footer,
  header,
  landing,
  organizations,
  practitioners,
  search
}
