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


export class CreateUserTagDto implements Partial<UserTagEntity> {
  
  @IsDefined()
  @IsInt()
id: number;
  @IsOptional()
  @IsString()
metadata?: string | null;
  @IsDefined()
  @IsString()
create_at: string;
  @IsOptional()
  @IsString()
updated_at?: string | null;
  @IsOptional()
  @IsString()
deleted_at?: string | null;
  @IsDefined()
  @IsInt()
user_id: number;
  @IsDefined()
  @IsInt()
tag_id: number;
}

        
