import {
  BuildOptions,
  CreateOptions,
  FindOptions,
  UpdateOptions,
  DestroyOptions,
  WhereOptions,
  Op,
  fn,
  Model,
  FindAttributeOptions,
  GroupOption,
  Includeable,
  Order,
  UpsertOptions,
  col
} from 'sequelize';
import {
  MapType,
  IPaginateModelsOptions,
  IRandomModelsOptions
} from "@app/shared";
import { ClassConstructor, plainToInstance } from 'class-transformer';
import { AppEnvironment, S3Objects } from '@app/backend';


export interface IModel<T extends {} = any> extends Model<T> {
  // readonly id: number;
  [key: string]: any;
}

export type MyModelStatic = typeof Model & {
  new (values?: object, options?: BuildOptions): IModel;
};

export type MyModelStaticTyped<T = any> = typeof Model<T> & {
  new (values?: object, options?: BuildOptions): IModel<T>;
};

export type MyModelStaticGeneric<T = any> = typeof Model & {
  new (values?: object, options?: BuildOptions): T;
};




export const convertModel = <T> (model: IModel | Model | null) => {
  return model ? (<any> model.toJSON()) as T : null;
}

export const convertModels = <T> (models: (IModel | Model)[]) => {
  return models.map((model) => (<any> model.toJSON()) as T);
}

export const convertModelCurry = <T> () => (model: IModel | Model | null) => {
  return model ? (<any> model.toJSON()) as T : null;
}

export const convertModelsCurry = <T> () => (models: (IModel | Model)[]) => {
  return models.map((model) => (<any> model.toJSON()) as T);
}


export async function paginateTable(model: MyModelStatic, options: IPaginateModelsOptions)  {
  const { user_id_field, user_id, min_id, include, attributes, group, whereClause, orderBy } = options;

  const useWhereClause: WhereOptions = <MapType> (!min_id
    ? { [user_id_field]: user_id }
    : { [user_id_field]: user_id, id: { [Op.lt]: min_id } }
  );
  if (whereClause) {
    Object.assign(useWhereClause, whereClause);
  }

  console.log(whereClause, { useWhereClause });

  const models: (Model | IModel)[] = await model.findAll({
    attributes,
    group,
    where: useWhereClause,
    include: include || [],
    limit: 5,
    order: orderBy || [['id', 'DESC']]
  });

  return models;
}

export async function getCount(
  model: MyModelStatic | Model,
  user_id_field: string,
  user_id: number,
  group?: GroupOption,
  whereClause?: WhereOptions,
)  {
  // const models = await model.findAll<Model<T>>({
  const useWhereClause = whereClause
    ? { ...whereClause, [user_id_field]: user_id }
    : { [user_id_field]: user_id };

  const models = await (model as MyModelStatic).count({
    group: group || [],
    where: useWhereClause,
  });

  return models;
}

export async function getAll(
  model: MyModelStatic | Model<any, any>,
  user_id_field: string,
  user_id: number,
  include?: Includeable[],
  attributes?: FindAttributeOptions,
  group?: GroupOption,
  whereClause?: WhereOptions,
  orderBy?: Order
)  {
  // const models = await model.findAll<Model<T>>({
  const useWhereClause = whereClause
    ? { ...whereClause, [user_id_field]: user_id }
    : { [user_id_field]: user_id };

  if (whereClause) {
    Object.assign(useWhereClause, whereClause);
  }
  console.log(whereClause, { useWhereClause });

  const models = await (model as MyModelStatic).findAll({
    attributes,
    group,
    where: useWhereClause,
    include: include || [],
    order: orderBy || [['id', 'DESC']]
  });

  return models;
}

export async function getById<T>(
  model: MyModelStatic | Model<any, any>,
  id: number,
  include?: Includeable[],
  attributes?: FindAttributeOptions,
  group?: GroupOption,
  whereClause?: WhereOptions,
)  {
  // const result = await model.findOne<Model<T>>({
  const useWhereClause = whereClause
    ? { ...whereClause, id }
    : { id };

  console.log(whereClause, { useWhereClause });

  const result = await (model as MyModelStatic).findOne({
    attributes,
    group,
    where: useWhereClause,
    include: include || [],
  });

  return result;
}

export async function getRandomModels<T>(model: MyModelStatic, params: IRandomModelsOptions) {
  const { limit, include, attributes, group } = params;

  try {
    const results = await (<any> model).findAll({
      limit: limit || 10,
      order: [fn( 'RANDOM' )],
      attributes,
      group,
      include,
    });

    return results;
  } 
  catch (e) {
    console.log(`get_random_models error - `, e);
    return null;
  }
}

export function get_recent_models<T = any>(
  model: MyModelStatic,
  whereClause: WhereOptions = {},
) {
  return model.findAll({
    where: whereClause,
    order: [['id', 'DESC']],
    limit: 20,
  })
  .then((models: Model[]) => {
    return convertModels<T>(<IModel[]> models);
  });
}





// converted

export async function paginateTableConverted<T>(
  model: MyModelStatic | Model<any, any>,
  user_id_field: string,
  user_id?: number,
  min_id?: number,
  include?: Includeable[],
  attributes?: FindAttributeOptions,
  group?: GroupOption,
  whereClause?: WhereOptions,
  orderBy?: Order
)  {
  const useWhereClause: WhereOptions = <MapType> (!min_id
    ? { [user_id_field]: user_id }
    : { [user_id_field]: user_id, id: { [Op.lt]: min_id } }
  );
  if (whereClause) {
    Object.assign(useWhereClause, whereClause);
  }

  console.log(whereClause, { useWhereClause });

  const models = await (model as MyModelStatic).findAll({
    attributes,
    group,
    where: useWhereClause,
    include: include || [],
    limit: 5,
    order: orderBy || [['id', 'DESC']]
  })
  .then((models: IModel[]) => {
    return convertModels<T>(models);
  });

  return models;
}

export async function getAllConverted<T>(
  model: MyModelStatic | Model<any, any>,
  user_id_field: string,
  user_id: number,
  include?: Includeable[],
  attributes?: FindAttributeOptions,
  group?: GroupOption,
  whereClause?: WhereOptions,
  orderBy?: Order
)  {
  // const models = await model.findAll<Model<T>>({
  const useWhereClause = whereClause
    ? { ...whereClause, [user_id_field]: user_id }
    : { [user_id_field]: user_id };

  if (whereClause) {
    Object.assign(useWhereClause, whereClause);
  }
  console.log(whereClause, { useWhereClause });

  const models = await (model as MyModelStatic).findAll({
    attributes,
    group,
    where: useWhereClause,
    include: include || [],
    order: orderBy || [['id', 'DESC']]
  });

  return models;
}

export async function getByIdConverted<T>(
  model: MyModelStatic | Model,
  id: number,
  include?: Includeable[],
  attributes?: FindAttributeOptions,
  group?: GroupOption,
  whereClause?: WhereOptions,
)  {
  // const result = await model.findOne<Model<T>>({
  const useWhereClause = whereClause
    ? { ...whereClause, id }
    : { id };

  console.log(whereClause, { useWhereClause });

  const result = await (model as MyModelStatic).findOne({
    attributes,
    group,
    where: useWhereClause,
    include: include || [],
  })
  .then((model: IModel | null) => {
    return convertModel<T>(model);
  });

  return result;
}

export async function getRandomModelsConverted<T>(
  model: MyModelStaticGeneric<T> | Model,
  limit: number,
  include?: Includeable[],
  attributes?: FindAttributeOptions,
  group?: GroupOption,
) {
  try {
    const results = await (<any> model).findAll({
      limit,
      order: [fn( 'RANDOM' )],
      attributes,
      group,
      include,
    })
    .then((models: IModel[]) => {
      return convertModels<T>(models);
    });

    return results;
  } 
  catch (e) {
    console.log(`get_random_models error - `, e);
    return null;
  }
}

export function get_recent_models_converted<T>(
  model: MyModelStatic | Model,
  whereClause: WhereOptions = {},
) {
  return (model as MyModelStatic).findAll({
    where: whereClause,
    order: [['id', 'DESC']],
    limit: 20,
  })
  .then((models) => {
    return convertModels<T>(<IModel[]> models);
  });
}

export const getS3ObjectInclude: (alias: string, key?: string) => Includeable = (alias: string, key: string = 'key') => {
  return {
    as: alias,
    model: S3Objects,
    attributes: {
      include: [
        [fn(`concat`, `${AppEnvironment.AWS.S3.SERVE_ORIGIN}/`, col(key)), 'public_url']
      ]
    }
  };
};




export interface IModelCrud<T> {
  create: (createObj: Partial<T>, createOptions?: CreateOptions<T>) => Promise<T | null>;
  findOne: (findOptions: FindOptions<T>) => Promise<T | null>;
  findAll: (findOptions: FindOptions<T>) => Promise<T[]>;
  findById: (id: number, findOptions?: FindOptions<T>) => Promise<T | null>;
  count: (findOptions: FindOptions<T>) => Promise<number>;

  update: (updateObj: Partial<T>, options: UpdateOptions<T>) => Promise<{ rows: number, models: T[] }>;
  updateById: (id: number, updateObj: Partial<T>) => Promise<{ rows: number, model: T | null }>;
  upsert: (data: Partial<T>, options: UpsertOptions<T>) => Promise<{ rowsAffected: boolean, model: T }>;

  destroy: (destroyOptions: DestroyOptions<T>) => Promise<{ results: number, models: T[] }>;
  delete: (destroyOptions: DestroyOptions<T>) => Promise<{ results: number, models: T[] }>;
  deleteById: (id: number) => Promise<{ results: number, model: T | null }>;

  paginate: (params: IPaginateModelsOptions) => Promise<T[]>;
  getAll: (params: {
    parent_id_field: string,
    parent_id: number,
    include?: Includeable[],
    attributes?: FindAttributeOptions,
    group?: GroupOption,
    whereClause?: WhereOptions<T>,
    orderBy?: Order
  }) => Promise<T[]>;

  randomModels: (params: IRandomModelsOptions) => Promise<T[]>;
}



export const sequelize_model_class_crud_to_entity_object = <T> (givenModelClass: MyModelStatic): IModelCrud<T> => {
  // console.log({ givenModelClass });
  if (!givenModelClass) {
    throw new Error(`Model is required...`);
  }

  const convertTypeCurry = (model: IModel | null) => {
    const data = !model ? null : model.toJSON() as T;
    // console.log(data);
    return data;
  };

  const convertTypeListCurry = (models: IModel[]) => models.map(convertTypeCurry);

  const convertTypeListCurryUntyped = (models: IModel[]) => convertTypeListCurry(models as any[]);

  const modelClass = givenModelClass as MyModelStatic;

  const create = (createObj: Partial<T>, createOptions?: CreateOptions<T>) => {
    return modelClass.create(createObj, createOptions).then(convertTypeCurry);
  };

  const count = (findOptions: FindOptions<T>) => {
    return modelClass.count(findOptions);
  };



  const findOne = (findOptions: FindOptions<T>) => {
    return modelClass.findOne(findOptions).then(convertTypeCurry);
  };
  const findById = (id: number, findOptions?: FindOptions<T>) => {
    const useWhere = findOptions
      ? { ...findOptions, where: { id } }
      : { where: { id } };
    return modelClass.findOne(useWhere).then(convertTypeCurry);
  };
  const findAll = (findOptions: FindOptions<T>) => {
    return modelClass.findAll(findOptions).then(convertTypeListCurry);
  };



  const update = (updateObj: Partial<T>, options: UpdateOptions<T>) => {
    return modelClass.update(updateObj, { ...options, returning: true })
      .then((updates) => ({ rows: updates[0], models: updates[1].map(convertTypeCurry) }));
  };
  const updateById = (id: number, updateObj: Partial<T>) => {
    return modelClass.update(updateObj, { where: { id }, returning: true })
      .then((updates) => ({
        rows: updates[0],
        model: updates[1][0] && convertTypeCurry(updates[1][0])
      }));
    // .then(async (updates) => {
    //   const fresh = await findById(id);
    //   // return updates;
    //   const returnValue = [updates[0], fresh] as [number, (T|null)];
    //   return returnValue;
    // });
  };
  const upsert = (data: Partial<T>, options: UpsertOptions<T>) => {
    return modelClass.upsert(data, options).then((updates) => ({ model: updates[0] && convertTypeCurry(updates[0]), rowsAffected: updates[1] }));
  };



  const deleteFn = async (destroyOptions: DestroyOptions<T>) => {
    const results = await modelClass.destroy(destroyOptions);
    const models = !destroyOptions.where ? [] : await modelClass.findAll({ where: destroyOptions.where, paranoid: false }).then(convertTypeListCurry);
    return { results, models };
  };
  const deleteById = async (id: number) => {
    const results = await modelClass.destroy({ where: { id } });
    const model = await modelClass.findOne({ where: { id }, paranoid: false }).then(convertTypeCurry);
    return { results, model };
  };


  const paginate = (params: IPaginateModelsOptions) => {
    return paginateTable(modelClass, params).then(convertTypeListCurryUntyped);
  };

  const randomModels = (params: IRandomModelsOptions) => {
    return getRandomModels<T>(modelClass, params).then(convertTypeListCurry);
  };

  const getAllModals = (params: {
    parent_id_field: string,
    parent_id: number,
    include?: Includeable[],
    attributes?: FindAttributeOptions,
    group?: GroupOption,
    whereClause?: WhereOptions<T>,
    orderBy?: Order
  }) => {
    const {
      parent_id_field,
      parent_id,
      include,
      attributes,
      group,
      whereClause,
      orderBy
    } = params;
    return getAll(
      modelClass,
      parent_id_field,
      parent_id,
      include,
      attributes,
      group,
      whereClause,
      orderBy
    ).then(convertTypeListCurry);
  };

  

  return {
    create,
  
    findOne,
    findAll,
    findById,
    count,

    update,
    updateById,
    upsert,

    destroy: deleteFn,
    delete: deleteFn,
    deleteById,

    paginate,
    getAll: getAllModals,
    randomModels,
  };

};

export const sequelize_model_class_crud_to_entity_class = <T> (givenModelClass: MyModelStatic, ModelEntity: ClassConstructor<T>): IModelCrud<T> => {
  // console.log({ givenModelClass });
  if (!givenModelClass) {
    throw new Error(`Model is required...`);
  }

  const convertTypeCurry = (model: IModel) => {
    const data = plainToInstance<T, MapType>(ModelEntity as ClassConstructor<T>, !model ? {} : model.toJSON()) as T;
    // console.log(data);
    return data;
  };
  const convertTypeListCurry = (models: IModel[]) => models.map(convertTypeCurry);


  const modelClass = givenModelClass as MyModelStatic;

  const create = (createObj: any, createOptions?: CreateOptions) => {
    return modelClass.create(createObj, createOptions).then(convertTypeCurry);
  };

  const count = (findOptions: FindOptions) => {
    return modelClass.count(findOptions);
  };



  const findOne = (findOptions: FindOptions) => {
    return modelClass.findOne(findOptions).then(convertTypeCurry);
  };
  const findById = (id: number, findOptions?: FindOptions) => {
    const useWhere = findOptions
      ? { ...findOptions, where: { id } }
      : { where: { id } };
    return modelClass.findOne(useWhere).then(convertTypeCurry);
  };
  const findAll = (findOptions: FindOptions) => {
    return modelClass.findAll(findOptions).then(convertTypeListCurry);
  };



  const update = (updateObj: any, options: UpdateOptions) => {
    return modelClass.update(updateObj, { ...options, returning: true })
      .then((updates) => ({ rows: updates[0], models: updates[1].map(convertTypeCurry) }));
  };
  const updateById = (id: number, updateObj: any) => {
    return modelClass.update(updateObj, { where: { id }, returning: true })
      .then((updates) => ({ rows: updates[0], model: updates[1][0] && convertTypeCurry(updates[1][0]) }));
    // .then(async (updates) => {
    //   const fresh = await findById(id);
    //   // return updates;
    //   const returnValue = [updates[0], fresh] as [number, (T|null)];
    //   return returnValue;
    // });
  };

  const upsert = (data: Partial<T>, options: UpsertOptions<T>) => {
    return modelClass.upsert(data, options).then((updates) => ({ model: updates[0] && convertTypeCurry(updates[0]), rowsAffected: updates[1] }));
  };



  const deleteFn = async (destroyOptions: DestroyOptions) => {
    const results = await modelClass.destroy(destroyOptions);
    const models = !destroyOptions.where ? [] : await modelClass.findAll({ where: destroyOptions.where, paranoid: false }).then(convertTypeListCurry);
    return { results, models };
  };
  const deleteById = async (id: number) => {
    const results = await modelClass.destroy({ where: { id } });
    const model = await modelClass.findOne({ where: { id }, paranoid: false }).then(convertTypeCurry);
    return { results, model };
  };


  const paginate = (params: IPaginateModelsOptions) => {
    return paginateTable(modelClass, params).then(convertTypeListCurry);
  };

  const randomModels = (params: IRandomModelsOptions) => {
    return getRandomModels<T>(modelClass, params).then(convertTypeListCurry);
  };

  const getAllModals = (params: {
    parent_id_field: string,
    parent_id: number,
    include?: Includeable[],
    attributes?: FindAttributeOptions,
    group?: GroupOption,
    whereClause?: WhereOptions,
    orderBy?: Order
  }) => {
    const {
      parent_id_field,
      parent_id,
      include,
      attributes,
      group,
      whereClause,
      orderBy
    } = params;
    return getAll(
      modelClass,
      parent_id_field,
      parent_id,
      include,
      attributes,
      group,
      whereClause,
      orderBy
    ).then(convertTypeListCurry);
  };

  

  return {
    create,
  
    findOne,
    findAll,
    findById,
    count,
    upsert,

    update,
    updateById,

    destroy: deleteFn,
    delete: deleteFn,
    deleteById,

    paginate,
    getAll: getAllModals,
    randomModels,

    // model: givenModelClass,
  };

};