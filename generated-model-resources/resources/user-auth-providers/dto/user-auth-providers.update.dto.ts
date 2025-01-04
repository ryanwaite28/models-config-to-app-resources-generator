import {
  UserAuthProviderEntity,
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


export class UpdateUserAuthProviderDto implements Partial<UserAuthProviderEntity> {
  
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
  details?: string | null;

  @IsDefined()
  @IsInt()
  user_id: number;

  @IsDefined()
  @IsString()
  provider_name: string;

  @IsDefined()
  @IsString()
  provider_id: string;

}

        
