import 'reflect-metadata';
import { Service, Inject } from "typedi";
import { IModelCrud } from "../lib/utils/sequelize.utils";
import {
  S3ObjectEntity,
  UserEntity,
  UserAuthProviderEntity,
  TagEntity,
  UserTagEntity,
} from '@app/shared';
import { S3_OBJECT_REPO_INJECT_TOKEN } from '../resources/s3-objects/s3-objects.repository';
import { USER_REPO_INJECT_TOKEN } from '../resources/users/users.repository';
import { USER_AUTH_PROVIDER_REPO_INJECT_TOKEN } from '../resources/user-auth-providers/user-auth-providers.repository';
import { TAG_REPO_INJECT_TOKEN } from '../resources/tags/tags.repository';
import { USER_TAG_REPO_INJECT_TOKEN } from '../resources/user-tags/user-tags.repository';

                                 
@Service()
export class RepositoryService {
                                 
  constructor(
    @Inject(S3_OBJECT_REPO_INJECT_TOKEN) public readonly s3ObjectRepo: IModelCrud<S3ObjectEntity>,
    @Inject(USER_REPO_INJECT_TOKEN) public readonly userRepo: IModelCrud<UserEntity>,
    @Inject(USER_AUTH_PROVIDER_REPO_INJECT_TOKEN) public readonly userAuthProviderRepo: IModelCrud<UserAuthProviderEntity>,
    @Inject(TAG_REPO_INJECT_TOKEN) public readonly tagRepo: IModelCrud<TagEntity>,
    @Inject(USER_TAG_REPO_INJECT_TOKEN) public readonly userTagRepo: IModelCrud<UserTagEntity>,
  ) {}
                                 
}
        
