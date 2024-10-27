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


export class UpdateUserDto implements Partial<UserEntity> {
  
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
stripe_customer_account_id?: string | null;
  @IsOptional()
  @IsString()
stripe_account_id?: string | null;
  @IsDefined()
  @IsBoolean()
stripe_account_verified: boolean;
  @IsDefined()
  @IsBoolean()
stripe_identity_verified: boolean;
  @IsOptional()
  @IsString()
first_name?: string | null;
  @IsOptional()
  @IsString()
last_name?: string | null;
  @IsOptional()
  @IsString()
bio?: string | null;
  @IsOptional()
  @IsInt()
icon_s3object_id?: number | null;
  @IsOptional()
  @IsString()
town?: string | null;
  @IsOptional()
  @IsString()
city?: string | null;
  @IsOptional()
  @IsString()
state?: string | null;
  @IsOptional()
  @IsInt()
zipcode?: number | null;
  @IsOptional()
  @IsString()
country?: string | null;
  @IsOptional()
  @IsString()
tags?: string | null;
  @IsOptional()
  @IsString()
specialties?: string | null;
  @IsDefined()
  @IsBoolean()
person_verified: boolean;
  @IsDefined()
  @IsBoolean()
email_verified: boolean;
  @IsDefined()
  @IsBoolean()
phone_verified: boolean;
}

        
