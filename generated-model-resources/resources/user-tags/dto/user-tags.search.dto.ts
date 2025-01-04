import {
  UserTagEntity,
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


export class SearchUserTagDto implements Partial<UserTagEntity> {
  
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
  @Matches(INTEGER_WITH_COMPARATOR_REGEX)
  user_id_op: string | null;
  

  @IsOptional()
  @IsString()
  @Matches(INTEGER_WITH_COMPARATOR_REGEX)
  tag_id_op: string | null;
  

}

        
