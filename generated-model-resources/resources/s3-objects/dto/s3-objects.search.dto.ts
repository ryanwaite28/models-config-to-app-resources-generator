import {
  S3ObjectEntity,
} from "@app/shared";
import {
  IsBoolean,
  IsEmail,
  IsIn,
  IsNotEmpty,
  IsDefined,
  IsOptional,
  IsString,
  IsNumber,
  IsInt,
  Matches,
  ValidateIf,
} from 'class-validator';
import {
  ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX,
  BOOLEAN_REGEX,
  INTEGER_WITH_COMPARATOR_REGEX,
} from "../../../regex/common.regex";


export class SearchS3ObjectDto implements Partial<S3ObjectEntity> {
  
  @IsOptional()
  @IsString()
  @Matches(INTEGER_WITH_COMPARATOR_REGEX)
id_op: string | null;

  @IsOptional()
  @IsString()
  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)
metadata: string | null;
  @IsOptional()
  @IsString()
  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)
create_at: string | null;
  @IsOptional()
  @IsString()
  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)
updated_at: string | null;
  @IsOptional()
  @IsString()
  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)
deleted_at: string | null;
  @IsOptional()
  @IsString()
  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)
model_type: string | null;
  @IsOptional()
  @IsString()
  @Matches(INTEGER_WITH_COMPARATOR_REGEX)
model_id_op: string | null;

  @IsOptional()
  @IsString()
  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)
mimetype: string | null;
  @IsOptional()
  @IsBoolean()
is_private: boolean | null;
  @IsOptional()
  @IsString()
  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)
region: string | null;
  @IsOptional()
  @IsString()
  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)
bucket: string | null;
  @IsOptional()
  @IsString()
  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)
key: string | null;
}

        
