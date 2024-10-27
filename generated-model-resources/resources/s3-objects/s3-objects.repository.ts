import 'reflect-metadata';
import {
  S3ObjectEntity,
} from "@app/shared";
import { sequelize_model_class_crud_to_entity_object, IModelCrud } from "../../lib/utils/sequelize.utils";
import { S3Objects } from '@app/backend';
import { Container, Token } from "typedi";




export const S3_OBJECT_REPO_INJECT_TOKEN = new Token<IModelCrud<S3ObjectEntity>>('S3_OBJECT_REPO_INJECT_TOKEN');

const S3ObjectsRepo: IModelCrud<S3ObjectEntity> = sequelize_model_class_crud_to_entity_object<S3ObjectEntity>(S3Objects);

Container.set(S3_OBJECT_REPO_INJECT_TOKEN, S3ObjectsRepo);
        
