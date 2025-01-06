export interface _BaseEntity {}






export interface S3ObjectEntity extends _BaseEntity {
  id: number;
  metadata: string | null;
  create_at: string;
  updated_at: string | null;
  deleted_at: string | null;
  model_type: string | null;
  model_id: number | null;
  mimetype: string | null;
  is_private: boolean;
  region: string;
  bucket: string;
  key: string;
}
  

export interface UserEntity extends _BaseEntity {
  id: number;
  metadata: string | null;
  create_at: string;
  updated_at: string | null;
  deleted_at: string | null;
  stripe_customer_account_id: string | null;
  stripe_account_id: string | null;
  stripe_account_verified: boolean;
  stripe_identity_verified: boolean;
  first_name: string | null;
  last_name: string | null;
  bio: string | null;
  icon_s3object_id: number | null;
  town: string | null;
  city: string | null;
  state: string | null;
  zipcode: number | null;
  country: string | null;
  tags: string | null;
  specialties: string | null;
  person_verified: boolean;
  email_verified: boolean;
  phone_verified: boolean;
  
  icon?: S3ObjectEntity;
  authProviders?: UserAuthProviderEntity[];
  user_tags?: TagEntity[];
}
  

export interface UserAuthProviderEntity extends _BaseEntity {
  id: number;
  metadata: string | null;
  create_at: string;
  updated_at: string | null;
  deleted_at: string | null;
  details: string | null;
  user_id: number;
  provider_name: string;
  provider_id: string;
  
  user?: UserEntity;
}
  

export interface TagEntity extends _BaseEntity {
  id: number;
  metadata: string | null;
  create_at: string;
  updated_at: string | null;
  deleted_at: string | null;
  name: string;
  description: string | null;
  
  users?: UserEntity[];
}
  

export interface UserTagEntity extends _BaseEntity {
  id: number;
  metadata: string | null;
  create_at: string;
  updated_at: string | null;
  deleted_at: string | null;
  user_id: number;
  tag_id: number;
  
  user?: UserEntity;
  tag?: TagEntity;
}
  