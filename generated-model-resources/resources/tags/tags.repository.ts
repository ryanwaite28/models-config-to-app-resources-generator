import 'reflect-metadata';
import {
  TagEntity,
} from "@app/shared";
import { sequelize_model_class_crud_to_entity_object, IModelCrud } from "../../lib/utils/sequelize.utils";
import { Tags } from '@app/backend';
import { Container, Token } from "typedi";




export const TAG_REPO_INJECT_TOKEN = new Token<IModelCrud<TagEntity>>('TAG_REPO_INJECT_TOKEN');

const TagsRepo: IModelCrud<TagEntity> = sequelize_model_class_crud_to_entity_object<TagEntity>(Tags);

Container.set(TAG_REPO_INJECT_TOKEN, TagsRepo);
        
