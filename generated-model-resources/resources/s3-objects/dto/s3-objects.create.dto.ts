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


export class CreateS3ObjectDto implements Partial<S3ObjectEntity> {
  
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

  @IsOptional()
  @IsString()
  model_type?: string | null;

  @IsOptional()
  @IsInt()
  model_id?: number | null;

  @IsOptional()
  @IsString()
  mimetype?: string | null;

  @IsDefined()
  @IsBoolean()
  is_private: boolean;

  @IsDefined()
  @IsString()
  region: string;

  @IsDefined()
  @IsString()
  bucket: string;

  @IsDefined()
  @IsString()
  key: string;

}

        
