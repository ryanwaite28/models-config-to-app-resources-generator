import {
  TagEntity,
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


export class CreateTagDto implements Partial<TagEntity> {
  
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
  @IsString()
  name: string;

  @IsOptional()
  @IsString()
  description?: string | null;

}

        
