export const AUTH_BEARER_HEADER_REGEX: RegExp = /Bearer\s[^]/;
export const GENERIC_TEXT_REGEX: RegExp = /^[a-zA-Z0-9\s'\-\_\.\@\$\#]{1,250}/;
export const PERSON_NAME_REGEX: RegExp = /^[a-zA-Z\s'\-\_\.]{2,50}$/;
export const URL_REGEX = /[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}([-a-zA-Z0-9()@:%_\+.~#?&//=]*)?/gi;
export const BASE64_REGEX = /^data:([A-Za-z-+\/]+);base64,(.+)$/;
export const MENTIONS_REGEX = /@[a-zA-Z0-9\-\_\.]{2,50}/gi;

export const YOUTUBE_URL_STANDARD = /http(s?):\/\/(www\.)?youtube\.com\/watch\?(.*)/gi;
export const YOUTUBE_URL_SHORT = /http(s?):\/\/(www\.)?youtu\.be\/(.*)/gi;
export const YOUTUBE_URL_EMBED = /http(s?):\/\/(www\.)?youtube\.com\/embed\/(.*)/gi;
export const YOUTUBE_URL_ID = /(v=[a-zA-Z0-9\-\_]{7,}|\/[a-zA-Z0-9\-\_]{7,})/gi;

export const LEADING_SPACES = /[\s]{2,}/;
export const LEADING_SPACES_GLOBAL = /[\s]{2,}/gi;

export const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
// export const PHONE_NUMBER_REGEX = /^\+?[1-9]\d{1,14}$/;
export const PHONE_NUMBER_REGEX = /^\+1\d{10}$/;
export const ZIP_CODE_REGEX = /^\d{5}$/;
export const IP_ADDRESS_REGEX = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/;
export const MAC_ADDRESS_REGEX = /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/;
export const UUID_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$/;
export const ISO_DATE_REGEX = /^\d{4}-\d{2}-\d{2}$/;
export const ISO_TIME_REGEX = /^\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?(?:Z|[+-]\d{2}:\d{2})?$/;
export const ISO_DATE_TIME_REGEX = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?(?:Z|[+-]\d{2}:\d{2})?$/;
export const ISO_OFFSET_REGEX = /^\d{2}:\d{2}$/;
export const COMMA_SEPARATED_LIST_REGEX = /^(\w+(?:\s*,\s*\w+)*)$/;
export const COMMA_SEPARATED_LIST_REGEX2 = /(([^,]+),?)/;
export const SEMICOLON_SEPARATED_LIST_REGEX = /^(\w+(?:\s*;\s*\w+)*)$/;

export const PERCENTAGE_REGEX = /^(\d{1,3}%)$/;
export const INTEGER_REGEX = /^(\d+)$/;
export const DECIMAL_REGEX = /^(\d+(?:\.\d*)?)$/;
export const TIME_REGEX = /^(\d{2}:\d{2}:\d{2})$/;
export const DATE_REGEX = /^(\d{4}-\d{2}-\d{2})$/;
export const DATETIME_REGEX = /^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})$/;
export const UUID_V4_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V5_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-5[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V6_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[6789AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V7_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-7[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V8_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-8[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V9_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-9[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V10_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-A[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V11_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-B[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V12_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-C[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;

export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_REGEX = /^[a-zA-Z0-9\s\-\_]{1,250}$/;
export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_REGEX = /^[a-zA-Z0-9\s\-\_\.\@]{1,250}$/;
export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_REGEX = /^[a-zA-Z0-9\s\-\_\.\,]{1,250}$/;
export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_REGEX = /^[a-zA-Z0-9\s\-\_\.\,\:]{1,250}$/;
export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX = /^[a-zA-Z0-9\s\-\_\.\,\:\/]{1,250}$/;
export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_BRACKET_REGEX = /^[a-zA-Z0-9\s\-\_\.\,\:\/\[\]]{1,250}$/;
export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_BRACKET_PARENTHESIS_REGEX = /^[a-zA-Z0-9\s\-\_\.\,\:\/\[\]\(\)]{1,250}$/;

export const BOOLEAN_REGEX = /^(true|false)$/;

export const INTEGER_WITH_COMPARATOR_REGEX = /(^(eq|ne|gt|lt|gte|lte)<(\d+)>$|^(between|notBetween)<([\d]+,[\d]+)>$|^(in|notIn)<([\d]+(,[\d]+)*)>$)/;
// day of the week regex
export const DAY_OF_WEEK_REGEX = /^(mon|tue|wed|thu|fri|sat|sun)$/;
// full day of the week regex
// export const FULL_DAY_OF_WEEK_REGEX = /^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$/;
export const DAYS_OF_THE_WEEK_REGEX = /^(?:sunday,?)?(?:monday,?)?(?:tuesday,?)?(?:wednesday,?)?(?:thursday,?)?(?:friday,?)?(?:saturday,?)?$/;
