import 'reflect-metadata';
import {
  UserAuthProviderEntity,
} from "@app/shared";
import { sequelize_model_class_crud_to_entity_object, IModelCrud } from "../../lib/utils/sequelize.utils";
import { UserAuthProviders } from '@app/backend';
import { Container, Token } from "typedi";




export const USER_AUTH_PROVIDER_REPO_INJECT_TOKEN = new Token<IModelCrud<UserAuthProviderEntity>>('USER_AUTH_PROVIDER_REPO_INJECT_TOKEN');

const UserAuthProvidersRepo: IModelCrud<UserAuthProviderEntity> = sequelize_model_class_crud_to_entity_object<UserAuthProviderEntity>(UserAuthProviders);

Container.set(USER_AUTH_PROVIDER_REPO_INJECT_TOKEN, UserAuthProvidersRepo);
        
