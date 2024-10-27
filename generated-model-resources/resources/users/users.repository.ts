import 'reflect-metadata';
import {
  UserEntity,
} from "@app/shared";
import { sequelize_model_class_crud_to_entity_object, IModelCrud } from "../../lib/utils/sequelize.utils";
import { Users } from '@app/backend';
import { Container, Token } from "typedi";




export const USER_REPO_INJECT_TOKEN = new Token<IModelCrud<UserEntity>>('USER_REPO_INJECT_TOKEN');

const UsersRepo: IModelCrud<UserEntity> = sequelize_model_class_crud_to_entity_object<UserEntity>(Users);

Container.set(USER_REPO_INJECT_TOKEN, UsersRepo);
        
