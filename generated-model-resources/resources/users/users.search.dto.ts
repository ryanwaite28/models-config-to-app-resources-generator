import {
  UserEntity,
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


export class SearchUserDto implements Partial<UserEntity> {
  
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
stripe_customer_account_id: string | null;
  @IsOptional()
  @IsString()
  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)
stripe_account_id: string | null;
  @IsOptional()
  @IsBoolean()
stripe_account_verified: boolean | null;
  @IsOptional()
  @IsBoolean()
stripe_identity_verified: boolean | null;
  @IsOptional()
  @IsString()
  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)
first_name: string | null;
  @IsOptional()
  @IsString()
  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)
last_name: string | null;
  @IsOptional()
  @IsString()
  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)
bio: string | null;
  @IsOptional()
  @IsString()
  @Matches(INTEGER_WITH_COMPARATOR_REGEX)
icon_s3object_id_op: string | null;

  @IsOptional()
  @IsString()
  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)
town: string | null;
  @IsOptional()
  @IsString()
  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)
city: string | null;
  @IsOptional()
  @IsString()
  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)
state: string | null;
  @IsOptional()
  @IsString()
  @Matches(INTEGER_WITH_COMPARATOR_REGEX)
zipcode_op: string | null;

  @IsOptional()
  @IsString()
  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)
country: string | null;
  @IsOptional()
  @IsString()
  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)
tags: string | null;
  @IsOptional()
  @IsString()
  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)
specialties: string | null;
  @IsOptional()
  @IsBoolean()
person_verified: boolean | null;
  @IsOptional()
  @IsBoolean()
email_verified: boolean | null;
  @IsOptional()
  @IsBoolean()
phone_verified: boolean | null;
}

        
