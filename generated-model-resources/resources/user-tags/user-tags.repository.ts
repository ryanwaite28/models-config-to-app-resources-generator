import 'reflect-metadata';
import {
  UserTagEntity,
} from "@app/shared";
import { sequelize_model_class_crud_to_entity_object, IModelCrud } from "../../lib/utils/sequelize.utils";
import { UserTags } from '@app/backend';
import { Container, Token } from "typedi";




export const USER_TAG_REPO_INJECT_TOKEN = new Token<IModelCrud<UserTagEntity>>('USER_TAG_REPO_INJECT_TOKEN');

const UserTagsRepo: IModelCrud<UserTagEntity> = sequelize_model_class_crud_to_entity_object<UserTagEntity>(UserTags);

Container.set(USER_TAG_REPO_INJECT_TOKEN, UserTagsRepo);
        
