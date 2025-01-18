import os, sys, re, json
from pathlib import Path
import lorem
from deepmerge import Merger



# https://pypi.org/project/deepmerge/
my_merger = Merger(
    # pass in a list of tuple, with the
    # strategies you are looking to apply
    # to each type.
    [
        (list, ["append"]),
        (dict, ["merge"]),
        (set, ["union"])
    ],
    # next, choose the fallback strategies,
    # applied to all other types:
    ["override"],
    # finally, choose the strategies in
    # the case where the types conflict:
    ["override"]
)

model_config_to_drizzle_type_map = {
  'string': 'varchar',
  'text': 'text',
  'integer': 'integer',
  'float': 'numeric',
  'boolean': 'boolean',
  'date': 'date',
  'datetime': 'timestamp',
  'time': 'time',
  'json': 'json',
  'jsonb': 'jsonb',
}

model_config_to_graphql_schema_type_map = {
  'string': 'String',
  'text': 'String',
  'integer': 'Int',
  'float': 'Float',
  'boolean': 'Boolean',
  'date': 'Date',
  'datetime': 'Date',
  'time': 'Date',
  'json': 'String',
  'jsonb': 'String',
}

model_config_to_graphql_object_type_map = {
  'string': 'GraphQLString',
  'text': 'GraphQLString',
  'integer': 'GraphQLInt',
  'float': 'GraphQLFloat',
  'boolean': 'GraphQLBoolean',
  'date': 'GraphQLDate',
  'datetime': 'GraphQLDate',
  'time': 'GraphQLDate',
  'json': 'GraphQLString',
  'jsonb': 'GraphQLString',
}

model_config_to_typescript_type_map = {
  'string': 'string',
  'text': 'string',
  'integer': 'number',
  'float': 'number',
  'boolean': 'boolean',
  'date': 'string',
  'datetime': 'string',
  'time': 'string',
  'json': 'string',
  'jsonb': 'string',
}

root_path = 'app/generated-src'

Path(root_path).mkdir(parents = True, exist_ok = True)



def camel_to_kebab(s):
    """Converts a camelCase string to kebab-case."""
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s).lower()
    return s
  
def camel_to_snake(s):
    """Converts a camelCase string to snake-case."""
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()
    return s
  
def pluralize(s: str) -> str:
  """Pluralizes a singular noun."""
  if s.endswith('s'):
    return s + 'es'
  elif s.endswith('ey'):
    return s + 's'
  elif s.endswith('y'):
    return s[:-1] + 'ies'
  else:
    return s + 's'
  
def format_updates_from_dto(f: str) -> str:
  '''
  f: str - a converted field name string from a sequelize model definition
  return example:
  
  name: dto.name,
  '''
  
  formatted = f"{f}: dto.{f},"
    
  # print ('formatted:')
  # print (formatted)

  return formatted


def format_dto_fields(f: str) -> str:
  decorated = (
    '  ' + ('@IsOptional()' if ('| null' in f) else '@IsDefined()') + '\n' + 
    '  ' + ('@IsString()' if (': string' in f) else '@IsBoolean()' if (': boolean' in f) else '@IsInt()' if (': number' in f) else '') + '\n' +
    '  ' + (f.replace(':', '?:') if ('| null' in f) else f) +
    '\n'
  )
    
  # print ('decorated:')
  # print (decorated)

  return decorated



def format_dto_fields_for_query(f: str) -> str:
  def format_number_field(f: str) -> str:
    return (
      '  ' + '@IsString()\n  @Matches(INTEGER_WITH_COMPARATOR_REGEX)\n' +
      '  ' + (f if ('| null' in f) else f.replace(';', ' | null;')).replace(':', '_op:').replace('number', 'string')
    )


  decorated = (
    '  @IsOptional()\n' + 
    ('  @IsString()\n  @Matches(ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX)' if (': string' in f) else '  @IsBoolean()' if (': boolean' in f) else format_number_field(f) if (': number' in f) else '') + '\n' +
    # + (f.split(':')[0] + ': string | null;')
    '  ' + ('' if (': number' in f) else (f if ('| null' in f) else f.replace(';', ' | null;')))
    + '\n'
  )
    
  # print ('decorated:')
  # print (decorated)

  return decorated



  
  
  
user_owner_field_by_model = {}

global_model_names: list[str] = []

field_names_by_model: dict[list[str]] = {}
field_configs_by_model: dict[dict] = {}
field_definitions_by_model: dict[list[str]] = {}
relationships_definitions = []


def makeModelVarName(model_name: str) -> str:
  return model_name[0].lower() + model_name[1:]


def create_openapi_specs_from_model(model_name: str):
  kebob_name = camel_to_kebab(model_name)
  snake_name = camel_to_snake(model_name)
  
  model_name_plural = pluralize(model_name)
  model_var_name = makeModelVarName(model_name)
  
  singular = model_name.lower()
  plural = (singular[:-1] + 'ies') if (singular[-1] == 'y') else (singular + 's')
  
  kebob_name_plural = pluralize(kebob_name)
  snake_name_plural = pluralize(snake_name)
  
  singular_caps = singular.capitalize()
  plural_caps = plural.capitalize()

  model_properties = {}
  
  example_config = {}

  required_fields = []


  for field_def in field_definitions_by_model.get(model_name, []):

    field_name: str = field_def.split(':')[0].replace(' ', '')

    field_type = "string" if (': string' in field_def) else "boolean" if (': boolean' in field_def) else "integer" if (': number' in field_def) else None
    field_format = "date-time" if (('date' in field_def) or ('time' in field_def) or ('_at' in field_def)) else "boolean" if (': boolean' in field_def) else "int64" if (': number' in field_def) else "string"

    if not ('| null' in field_def):
      required_fields.append(field_name)

    model_field_property_config = {
      "type": field_type,
      "format": field_format,
      # "required": not ('| null' in field_def),
      # "nullable": ('| null' in field_def),
      "description": field_name.replace('_', ' ').capitalize()
    }

    model_properties[field_name] = model_field_property_config

    example_config[field_name] = "2024-01-01T00:00:00Z" if (field_type == "date-time") else "" if (field_type == 'string') else 1 if (field_type == 'integer') else True if (field_type == 'boolean') else None

  schema_definition = {
    f"{model_name}Entity": {
      "type": "object",
      "description": f"{model_name} entity",
      "properties": model_properties,
      "required": required_fields
    },
    f"Create{model_name}Dto": {
      "type": "object",
      "description": f"Create {model_name} DTO",
      "properties": model_properties
    },
    f"Update{model_name}Dto": {
      "type": "object",
      "description": f"Update {model_name} DTO",
      "properties": model_properties
    },
    f"Search{model_name}Dto": {
      "type": "object",
      "description": f"Search {model_name} DTO",
      "properties": model_properties
    }
  }

  specs = {
    "paths": {
      f"/{kebob_name_plural}": {
        "get": {
          "tags": [f"{model_name}"],
          "summary": f"Get all {model_name_plural}",
          "description": f"Get all {model_name_plural}",
          "operationId": f"get{model_name_plural}",
          "parameters": [],
          "responses": {
            "200": {
              "description": f"List of {model_name_plural}",
              "content": {
                "application/json": {
                  "schema": {
                    "type": "array",
                    "items": {
                      "$ref": f"#/components/schemas/{model_name}Entity"
                    }
                  }
                }
              }
            }
          }
        },
        "post": {
          "tags": [f"{model_name}"],
          "summary": f"Create a new {model_name}",
          "description": f"Create a new {model_name}",
          "operationId": f"create{model_name}",
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": f"#/components/schemas/Create{model_name}Dto"
                },
                "example": example_config
              }
            }
          },
          "responses": {
            "201": {
              "description": f"Created {model_name}",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": f"#/components/schemas/{model_name}Entity"
                  }
                }
              }
            }
          }
        }
      },
      f"/{kebob_name_plural}/search": {
        "get": {
          "tags": [f"{model_name}"],
          "summary": f"Get {model_name_plural} by search",
          "description": f"Get {plural} by search",
          "operationId": f"search{model_name_plural}",
          "parameters": [],
          "responses": {
            "200": {
              "description": f"List of {model_name_plural}",
              "content": {
                "application/json": {
                  "schema": {
                    "type": "array",
                    "items": {
                      "$ref": f"#/components/schemas/Search{model_name}Dto"
                    }
                  }
                }
              }
            }
          }
        },
      },
      
      f"/{kebob_name_plural}/{{id}}": {
        "get": {
          "tags": [f"{model_name}"],
          "summary": f"Get {model_name} by ID",
          "description": f"Get {model_name} by ID",
          "operationId": f"get{model_name}ById",
          "parameters": [
            {
              "name": "id",
              "in": "path",
              "description": "ID of {model_name}",
              "required": True,
              "schema": {
                "type": "integer",
                "format": "int64"
              }
            }
          ],
          "responses": {
            "200": {
              "description": f"{model_name} found",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": f"#/components/schemas/{model_name}Entity"
                  }
                }
              }
            },
            "404": {
              "description": f"{singular_caps} not found"
            }
          }
        },
        "put": {
          "tags": [f"{model_name}"],
          "summary": f"Update {model_name} by ID",
          "description": f"Update {model_name} by ID",
          "operationId": f"update{model_name}",
          "parameters": [
            {
              "name": "id",
              "in": "path",
              "description": "ID of {model_name}",
              "required": True,
              "schema": {
                "type": "integer",
                "format": "int64"
              }
            }
          ],
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": f"#/components/schemas/Update{model_name}Dto"
                },
                "example": example_config
              }
            }
          },
          "responses": {
            "200": {
              "description": f"{model_name} updated",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": f"#/components/schemas/{model_name}Entity"
                  }
                }
              }
            },
            "404": {
              "description": f"{model_name} not found"
            }
          }
        },
        "patch": {
          "tags": [f"{model_name}"],
          "summary": f"Patch {model_name} by ID",
          "description": f"Patch {model_name} by ID",
          "operationId": f"Patch{model_name}",
          "parameters": [
            {
              "name": "id",
              "in": "path",
              "description": "ID of {model_name}",
              "required": True,
              "schema": {
                "type": "integer",
                "format": "int64"
              }
            }
          ],
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": f"#/components/schemas/Update{model_name}Dto"
                },
                "example": example_config
              }
            }
          },
          "responses": {
            "200": {
              "description": f"{model_name} updated",
              "content": {
                "application/json": {
                  "schema": {
                    "$ref": f"#/components/schemas/{model_name}Entity"
                  }
                }
              }
            },
            "404": {
              "description": f"{model_name} not found"
            }
          }
        },
        "delete": {
          "tags": [f"{model_name}"],
          "summary": f"Delete {model_name} by ID",
          "description": f"Delete {model_name} by ID",
          "operationId": f"delete{model_name}",
          "parameters": [
            {
              "name": "id",
              "in": "path",
              "description": "ID of {model_name}",
              "required": True,
              "schema": {
                "type": "integer",
                "format": "int64"
              }
            }
          ],
          "responses": {
            "204": {
              "description": f"{model_name} deleted"
            },
            "404": {
              "description": f"{model_name} not found"
            }
          }
        }
      }
    },
    "components": {
      "schemas": schema_definition
    }
  }

  


  return specs
  
  
def create_resource(
  model_name: str
):
    
  kebob_name = camel_to_kebab(model_name)
  snake_name = camel_to_snake(model_name)
  
  model_name_plural = pluralize(model_name)
  model_var_name = model_name[0].lower() + model_name[1:]
  
  singular = model_name.lower()
  plural = (singular[:-1] + 'ies') if (singular[-1] == 'y') else (singular + 's')
  
  kebob_name_plural = pluralize(kebob_name)
  snake_name_plural = pluralize(snake_name)
  
  singular_caps = singular.capitalize()
  plural_caps = plural.capitalize()
  
  base_path = f'{root_path}/resources'



  # if os.path.exists(base_path + f"/{kebob_name_plural}"):
  #   # print(f"Resource \"{model_name}\" already exists/created; exiting...")
  #   return


  Path(f"{base_path}/{kebob_name_plural}").mkdir(parents = True, exist_ok = True)
  Path(f"{base_path}/{kebob_name_plural}/dto").mkdir(parents = True, exist_ok = True)


  # files to create
  controller_file = Path(f"{base_path}/{kebob_name_plural}/{kebob_name_plural}.controller.ts")
  service_file = Path(f"{base_path}/{kebob_name_plural}/{kebob_name_plural}.service.ts")
  guard_file = Path(f"{base_path}/{kebob_name_plural}/{kebob_name_plural}.guard.ts")
  repository_file = Path(f"{base_path}/{kebob_name_plural}/{kebob_name_plural}.repository.ts")
  create_dto_file = Path(f"{base_path}/{kebob_name_plural}/dto/{kebob_name_plural}.create.dto.ts")
  update_dto_file = Path(f"{base_path}/{kebob_name_plural}/dto/{kebob_name_plural}.update.dto.ts")
  search_dto_file = Path(f"{base_path}/{kebob_name_plural}/dto/{kebob_name_plural}.search.dto.ts")
  
  
  controller_contents = (f'''\
import 'reflect-metadata';
import {{
  Controller,
  Param,
  QueryParam,
  QueryParams,                 
  Body,
  BodyParam,
  Get,
  Post,
  Put,
  Delete,
  Patch,
  UseBefore,
}} from 'routing-controllers';
import {{ OpenAPI }} from 'routing-controllers-openapi'
import {{ {model_name}Service }} from './{kebob_name_plural}.service';
import {{
  {model_name}Exists,
  AuthUserOwns{model_name}
}} from './{kebob_name_plural}.guard';
import {{ Create{model_name}Dto }} from "./dto/{kebob_name_plural}.create.dto";
import {{ Update{model_name}Dto }} from "./dto/{kebob_name_plural}.update.dto";
import {{ Search{model_name}Dto }} from "./dto/{kebob_name_plural}.search.dto";
import {{ JwtAuthorized }} from '../../middlewares/jwt.middleware';
import {{ JwtUser }} from '../../decorators/jwt.decorator';
import {{ {model_name} }} from '@app/shared';
import {{ MapType, JwtUserData }} from '@app/shared';
import {{ FileUpload, FileUploadByName }} from '../../decorators/file-upload.decorator';
import {{ UploadedFile }} from 'express-fileupload';
import {{ Service }} from 'typedi';



@Controller('/web/{kebob_name_plural}')
@Controller('/mobile/{kebob_name_plural}')
@Controller('/api/{kebob_name_plural}')
@Service()
export class {model_name}Controller {{
  
  constructor(private {model_var_name}Service: {model_name}Service) {{}}

  

  @Get('/search')
  @OpenAPI({{
    description: 'Search {model_name_plural}',
    responses: {{
      '200': {{
        description: 'Search Successful',
        content: {{
          'application/json': {{
            schema: {{
              type: 'array',
              items: {{
                '$ref': '#/components/schemas/{model_name}'
              }}
            }}
          }}
        }}
      }}
    }},
  }})
  get{model_name}BySearch(@QueryParams() query: Search{model_name}Dto) {{
    return this.{model_var_name}Service.get{model_name}BySearch(query);
  }}

  @Get('/:id')
  @OpenAPI({{
    description: 'Get {model_name} by id',
    responses: {{
      '200': {{
        description: 'Get Successful',
        content: {{
          'application/json': {{
            schema: {{
              '$ref': '#/components/schemas/{model_name}'
            }}
          }}
        }}
      }}
    }},
  }})
  get{model_name}ById(@Param('id') id: number) {{
    return this.{model_var_name}Service.get{model_name}ById(id);
  }}

  @Post('')
  @UseBefore(JwtAuthorized)
  @OpenAPI({{
    description: 'Create {model_name}',
    responses: {{
      '201': {{
        description: 'Post Successful',
        content: {{
          'application/json': {{
            schema: {{
              '$ref': '#/components/schemas/{model_name}'
            }}
          }}
        }}
      }}
    }},
  }})
  create{model_name}(
    @JwtUser() user: JwtUserData,
    @BodyParam('payload', {{ validate: true }}) dto: Create{model_name}Dto,
    @FileUpload() files: MapType<UploadedFile>
  ) {{
    return this.{model_var_name}Service.create{model_name}(user.id, dto, files);
  }}

  @Put('/:id')
  @UseBefore(JwtAuthorized)
  @OpenAPI({{
    description: 'Overwrite {model_name} by id',
    responses: {{
      '200': {{
        description: 'Put Successful',
        content: {{
          'application/json': {{
            schema: {{
              '$ref': '#/components/schemas/{model_name}'
            }}
          }}
        }}
      }}
    }},
  }})
  update{model_name}(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({{ validate: true }}) dto: Update{model_name}Dto
  ) {{
    return this.{model_var_name}Service.update{model_name}(user.id, id, dto);
  }}

  @Patch('/:id')
  @UseBefore(JwtAuthorized)
  @OpenAPI({{
    description: 'Update {model_name} by id',
    responses: {{
      '200': {{
        description: 'Patch Successful',
        content: {{
          'application/json': {{
            schema: {{
              '$ref': '#/components/schemas/{model_name}'
            }}
          }}
        }}
      }}
    }},
  }})
  patch{model_name}(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number,
    @Body({{ validate: true }}) dto: Update{model_name}Dto
  ) {{
    return this.{model_var_name}Service.patch{model_name}(user.id, id, dto);
  }}

  @Delete('/:id')
  @UseBefore(JwtAuthorized)
  @OpenAPI({{
    description: 'Delete {model_name} by id',
    responses: {{
      '204': {{
        description: 'Delete Successful'
      }}
    }},
  }})
  delete{model_name}(
    @JwtUser() user: JwtUserData,
    @Param('id') id: number
  ) {{
    return this.{model_var_name}Service.delete{model_name}(user.id, id);
  }}
        
}}''')
  


  guard_contents = (f'''\
import {{ NextFunction, Request, Response }} from 'express';
import {{
  HttpStatusCodes,
  {model_name}Entity,
}} from '@app/shared';
import {{ Container }} from "typedi";
import {{ {snake_name.upper()}_REPO_INJECT_TOKEN }} from "./{kebob_name_plural}.repository";



export async function {model_name}Exists(
  request: Request,
  response: Response,
  next: NextFunction
) {{
  const id = parseInt(request.params.id, 10);
  const {model_var_name}Repo = Container.get({snake_name.upper()}_REPO_INJECT_TOKEN);
  const {model_var_name}: {model_name}Entity = await {model_var_name}Repo.findOne({{ where: {{ id }} }});
  if (!{model_var_name}) {{
    return response.status(HttpStatusCodes.NOT_FOUND).json({{
      message: `{model_name} does not exist by id: ${{ id }}`
    }});
  }}
  response.locals.{model_var_name} = {model_var_name};
  return next();
}}

export async function AuthUserOwns{model_name}(
  request: Request,
  response: Response,
  next: NextFunction
) {{
  /* TODO: implement user ownership check 
  const {model_var_name} = response.locals.{model_var_name} as {model_name}Entity;
  const isOwner = {model_var_name}.{user_owner_field_by_model.get(model_name, 'owner_id')} === request['auth'].id;
  if (!isOwner) {{
    return response.status(HttpStatusCodes.FORBIDDEN).json({{
      message: `User is not owner of {model_name} by id: ${{ {model_var_name}.id }}`
    }});
  }}
  return next();
  */
}}



''')
  

  service_contents = (f'''\
import 'reflect-metadata';
import {{
  HttpStatusCodes,
  UserEntity,
  JwtUserData,
  S3ObjectEntity,
  {model_name}Entity,
  MapType,
}} from "@app/shared";
import {{ Create{model_name}Dto }} from "./dto/{kebob_name_plural}.create.dto";
import {{ Update{model_name}Dto }} from "./dto/{kebob_name_plural}.update.dto";
import {{ Search{model_name}Dto }} from "./dto/{kebob_name_plural}.search.dto";
import {{ UploadedFile }} from "express-fileupload";
import {{ AwsS3Service, AwsS3UploadResults }} from "../../services/s3.aws.service";
import {{ ModelTypes }} from "../../lib/constants/model-types.enum";
import {{
  LOGGER,
  S3Objects,
  createTransaction,
  HttpRequestException,
  AppEnvironment
}} from '@app/backend';
import {{ Includeable, col, literal }} from "sequelize";
import {{ Service, Inject }} from 'typedi';
import {{ getS3ObjectInclude }} from "../../lib/utils/sequelize.utils";
import {{ SocketIoService }} from '../../services/socket-io.service';
import {{ parseQueryParams }} from '../../lib/utils/query-parser.utils';
import {{ INTEGER_REGEX }} from '../../regex/common.regex';
import {{ RepositoryService }} from '../../services/repository.service';



export interface I{model_name}Service {{
  get{model_name}ById({snake_name}_id: number): Promise<{model_name}Entity>;
  get{model_name}BySearch(query: Search{model_name}Dto): Promise<{model_name}Entity[]>;
  create{model_name}(user_id: number, dto: Create{model_name}Dto, files?: MapType<UploadedFile>): Promise<{model_name}Entity>;
  update{model_name}(user_id: number, {snake_name}_id: number, dto: Update{model_name}Dto): Promise<{{ rows: number }}>;
  patch{model_name}(user_id: number, {snake_name}_id: number, dto: Update{model_name}Dto): Promise<{{ rows: number }}>;
  delete{model_name}(user_id: number, {snake_name}_id: number): Promise<{{ rows: number }}>;
}}


@Service()
export class {model_name}Service implements I{model_name}Service {{
  
  constructor(
    private repositoryService: RepositoryService,
    private awsS3Service: AwsS3Service,
    private socketService: SocketIoService,
  ) {{}}

  async get{model_name}ById({snake_name}_id: number) {{
    return this.repositoryService.{model_var_name}Repo.findOne({{
      where: {{ id: {snake_name}_id }}
    }});
  }}

  async get{model_name}BySearch(query: Search{model_name}Dto) {{
    const parsedParams = parseQueryParams(query);
    // LOGGER.info('parsedParams', {{ parsedParams }});
    const useLimit: number = (query['limit'] && INTEGER_REGEX.test(query['limit']))
      ? Math.min(100, parseInt(query['limit'], 10))
      : 10;
    return this.repositoryService.{model_var_name}Repo.findAll({{
      where: parsedParams,
      limit: useLimit
    }});
  }}
  
  async create{model_name}(user_id: number, dto: Create{model_name}Dto, files?: MapType<UploadedFile>) {{
    const s3Uploads: AwsS3UploadResults[] = [];
    let new_{snake_name}_id: number = null;
    
    try {{
      // start a new database transaction
      await createTransaction(async (transaction) => {{
        
        // create the {model_name} record
        const new_{snake_name} = await this.repositoryService.{model_var_name}Repo.create({{
          {'\n          '.join([ (format_updates_from_dto(f)) for f in field_names_by_model.get(model_name, []) ])}
        }}, {{ transaction }});
        
        new_{snake_name}_id = new_{snake_name}.id;
        
        if (files) {{
          /* Upload single file if needed
          const media_key = 'media';
          
          if (files[media_key]) {{
            const file: UploadedFile = files[media_key];
            const s3UploadResults: AwsS3UploadResults = await this.awsS3Service.uploadFile(file);
            s3Uploads.push(s3UploadResults);

            const s3Object = await this.repositoryService.s3ObjectRepo.create({{
              model_type: ModelTypes.{snake_name.upper()},
              model_id: new_{snake_name}.id,
              mimetype: file.mimetype,
              is_private: false,
              region: s3UploadResults.Region,
              bucket: s3UploadResults.Bucket,
              key: s3UploadResults.Key,
            }}, {{ transaction }});

            await this.repositoryService.{model_var_name}Repo.update({{ media_id: s3Object.id }}, {{ where: {{ id: new_{snake_name}.id }}, transaction }});
          }}
          */

          /* Upload multiple files if needed
          const mediasKey = '{snake_name}_media';
          const useFiles: UploadedFile[] = !files[mediasKey]
            ? []
            : Array.isArray(files[mediasKey])
              ? files[mediasKey]
              : [files[mediasKey]];

          for (const file of useFiles) {{
            const s3UploadResults: AwsS3UploadResults = await this.awsS3Service.uploadFile(file);
            s3Uploads.push(s3UploadResults);

            const s3Object = await this.repositoryService.s3ObjectRepo.create({{
              model_type: ModelTypes.{snake_name.upper()},
              model_id: new_{snake_name}.id,
              mimetype: file.mimetype,
              is_private: false,
              region: s3UploadResults.Region,
              bucket: s3UploadResults.Bucket,
              key: s3UploadResults.Key,
            }}, {{ transaction }});

            const new_{snake_name}_media = await this.repositoryService.___.create({{
              {snake_name}_id: new_{snake_name}.id,
              media_id: s3Object.id,
              description: ''
            }}, {{ transaction }});
          }}
          */
        }}
        
      }});
      
      const {snake_name} = await this.repositoryService.{model_var_name}Repo.findOne({{
        where: {{ id: new_{snake_name}_id }}
      }});

      return {snake_name};
    }}
    catch (error) {{
      // transaction rollback; delete all uploaded s3 objects
      if (s3Uploads.length > 0) {{
        for (const s3Upload of s3Uploads) {{
          this.awsS3Service.deleteObject(s3Upload)
          .catch((error) => {{
            LOGGER.error('s3 delete object error', {{ error, s3Upload }});
          }});
        }}
      }}

      LOGGER.error('Error creating {model_name}', error);
      throw new HttpRequestException(HttpStatusCodes.INTERNAL_SERVER_ERROR, {{
        message: 'Could not create {model_name}',
        context: error
      }});
    }}
    
  }}
  
  async update{model_name}(user_id: number, {snake_name}_id: number, dto: Update{model_name}Dto) {{
    const updates = await this.repositoryService.{model_var_name}Repo.update({{
      {'\n      '.join([ (format_updates_from_dto(f)) for f in field_names_by_model.get(model_name, []) ])}
    }}, {{
      where: {{
        id: {snake_name}_id,{(f"\n        {user_owner_field_by_model.get(model_name, 'owner_id')}: user_id") if (model_name in user_owner_field_by_model) else ''}
      }}
    }});
    return {{ rows: updates.rows }};
  }}
  
  async patch{model_name}(user_id: number, {snake_name}_id: number, dto: Update{model_name}Dto) {{
    const updateData = {{ ...dto }};
    Object.keys(updateData).forEach((key) => {{
      const isEmpty = (updateData[key] === null || updateData[key] === undefined);
      if (isEmpty) {{
        delete updateData[key]
      }}
    }});
    const updates = await this.repositoryService.{model_var_name}Repo.update(updateData, {{
      where: {{
        id: {snake_name}_id,{(f"\n        {user_owner_field_by_model.get(model_name, 'owner_id')}: user_id") if (model_name in user_owner_field_by_model) else ''}
      }}
    }});
    return {{ rows: updates.rows }};
  }}
  
  async delete{model_name}(user_id: number, {snake_name}_id: number) {{
    const deletes = await this.repositoryService.{model_var_name}Repo.destroy({{ 
      where: {{
        id: {snake_name}_id,{(f"\n        {user_owner_field_by_model.get(model_name, 'owner_id')}: user_id") if (model_name in user_owner_field_by_model) else ''}
      }}
    }});
    return {{ rows: deletes.results }};
  }}
        
}}''')
  


  repository_contents = (f'''\
import 'reflect-metadata';
import {{
  {model_name}Entity,
}} from "@app/shared";
import {{ sequelize_model_class_crud_to_entity_object, IModelCrud }} from "../../lib/utils/sequelize.utils";
import {{ {model_name_plural} }} from '@app/backend';
import {{ Container, Token }} from "typedi";




export const {snake_name.upper()}_REPO_INJECT_TOKEN = new Token<IModelCrud<{model_name}Entity>>('{snake_name.upper()}_REPO_INJECT_TOKEN');

const {model_name_plural}Repo: IModelCrud<{model_name}Entity> = sequelize_model_class_crud_to_entity_object<{model_name}Entity>({model_name_plural});

Container.set({snake_name.upper()}_REPO_INJECT_TOKEN, {model_name_plural}Repo);
        
''')



  create_dto_contents = (f'''\
import {{
  {model_name}Entity,
}} from "@app/shared";
import {{
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
}} from 'class-validator';


export class Create{model_name}Dto implements Partial<{model_name}Entity> {{
  
{'\n'.join([ format_dto_fields(f) for f in field_definitions_by_model.get(model_name, []) ])}
}}

        
''')
    
    
    
  
    

  update_dto_contents = (f'''\
import {{
  {model_name}Entity,
}} from "@app/shared";
import {{
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
}} from 'class-validator';


export class Update{model_name}Dto implements Partial<{model_name}Entity> {{
  
{'\n'.join([ format_dto_fields(f) for f in field_definitions_by_model.get(model_name, []) ])}
}}

        
''')
  

  search_dto_contents = (f'''\
import {{
  {model_name}Entity,
}} from "@app/shared";
import {{
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
}} from 'class-validator';
import {{
  ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX,
  BOOLEAN_REGEX,
  INTEGER_WITH_COMPARATOR_REGEX,
}} from "../../../regex/common.regex";


export class Search{model_name}Dto implements Partial<{model_name}Entity> {{
  
{'\n'.join([ format_dto_fields_for_query(f) for f in field_definitions_by_model.get(model_name, []) ])}
}}

        
''')





  if not controller_file.is_file():
    with open(controller_file, 'w') as f:
      f.write(controller_contents)
    
  if not guard_file.is_file():
    with open(guard_file, 'w') as f:
      f.write(guard_contents)
    
  if not service_file.is_file():
    with open(service_file, 'w') as f:
      f.write(service_contents)
    
  if not repository_file.is_file():
    with open(repository_file, 'w') as f:
      f.write(repository_contents)
    
  if not create_dto_file.is_file():
    with open(create_dto_file, 'w') as f:
      f.write(create_dto_contents)
    
  if not update_dto_file.is_file():
    with open(update_dto_file, 'w') as f:
      f.write(update_dto_contents)
    
  if not search_dto_file.is_file():
    with open(search_dto_file, 'w') as f:
      f.write(search_dto_contents)


  # add copy to src for reference
  
  Path(f"{root_path}/resources/{kebob_name_plural}").mkdir(parents = True, exist_ok = True)
  Path(f"{root_path}/resources/{kebob_name_plural}/dto").mkdir(parents = True, exist_ok = True)
  Path(f"{root_path}/resources/{kebob_name_plural}/dto/validations").mkdir(parents = True, exist_ok = True)

  with open(Path(f"{root_path}/resources/{kebob_name_plural}/{kebob_name_plural}.controller.ts"), 'w') as f:
    f.write(controller_contents)
  
  with open(Path(f"{root_path}/resources/{kebob_name_plural}/{kebob_name_plural}.guard.ts"), 'w') as f:
    f.write(guard_contents)
  
  with open(Path(f"{root_path}/resources/{kebob_name_plural}/{kebob_name_plural}.service.ts"), 'w') as f:
    f.write(service_contents)
  
  with open(Path(f"{root_path}/resources/{kebob_name_plural}/{kebob_name_plural}.repository.ts"), 'w') as f:
    f.write(repository_contents)
  
  with open(Path(f"{root_path}/resources/{kebob_name_plural}/dto/{kebob_name_plural}.create.dto.ts"), 'w') as f:
    f.write(create_dto_contents)
  
  with open(Path(f"{root_path}/resources/{kebob_name_plural}/dto/{kebob_name_plural}.update.dto.ts"), 'w') as f:
    f.write(update_dto_contents)
  
  with open(Path(f"{root_path}/resources/{kebob_name_plural}/dto/{kebob_name_plural}.search.dto.ts"), 'w') as f:
    f.write(search_dto_contents)
  


def getFieldDef(field, field_config):
  return f'{field}: {'string' if (field_config['dataType'] in ['string', 'text', 'datetime', 'uuid', 'json', 'jsonb']) else 'number' if (field_config['dataType'] in ['integer', 'float', 'double', 'number']) else 'boolean'}{' | null' if not (field_config['required']) else ''};'


def getGraphqlSchemaType(model, field_name):
  field_config = field_configs_by_model[model][field_name]
  schema_type = model_config_to_graphql_schema_type_map[field_config['dataType']]
  return schema_type

def getGraphqlObjectType(model, field_name):
  field_config = field_configs_by_model[model][field_name]
  object_type = model_config_to_graphql_object_type_map[field_config['dataType']]
  return object_type


def getTypeScriptType(model, field_name):
  field_config = field_configs_by_model[model][field_name]
  typescript_type = model_config_to_typescript_type_map[field_config['dataType']]
  return typescript_type


def getDrizzleDef(model: str, field_name: str):
  field_config = field_configs_by_model[model][field_name]
  if (field_config['dataType'] == 'integer') and ('primaryKey' in field_config) and field_config['primaryKey'] == True:
    return "integer().primaryKey().generatedAlwaysAsIdentity(),"
  
  column_def = ""
  
  drizzle_type = model_config_to_drizzle_type_map[field_config['dataType']]

  column_def += f"{drizzle_type}({ f"{{ minLength: {field_config['minLength']}, maxLength: {field_config['maxLength']} }}" if ('minLength' in field_config and 'maxLength' in field_config) else f"{{ minLength: {field_config['minLength']} }}" if ('minLength' in field_config) else f"{{ maxLength: {field_config['maxLength']} }}" if ('maxLength' in field_config) else "" })"

  if ('required' in field_config) and (field_config['required']):
    column_def += ".notNull()"

  if ('unique' in field_config) and (field_config['unique']):
    column_def += ".unique()"

  if ('defaultValue' in field_config):
    if field_config['defaultValue'] == None:
      column_def += ".default(null)"
    elif field_config['defaultValue'] == "now":
      column_def += ".defaultNow()"
    else:
      column_def += f".default({ f"\"{field_config['defaultValue']}\"" if (field_config['dataType'] in ['string', 'text', 'time', 'date', 'datetime']) else 'false' if (field_config['defaultValue'] == False) else 'true' if (field_config['defaultValue'] == True) else "null" if (field_config['defaultValue'] == None) else field_config['defaultValue'] })"

  column_def += ","

  return column_def


def convert_models_to_resources():
  
  global user_owner_field_by_model
  global field_definitions_by_model
  global field_names_by_model
  global field_configs_by_model
  global global_model_names



  openapi_specs = {
    "openapi": "3.0.0",
    "info": {
      "title": "Denaly | API",
      "description": "Swagger UI for Denaly API",
      "termsOfService": "https://example.com/terms/",
      "contact": {
        "name": "API Support",
        "url": "https://www.example.com/support",
        "email": "support@example.com"
      },
      "license": {
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
      },
      "version": "1.0.1"
    },
    "servers": [
      {
        "url": "http://localhost:4000/web",
        "description": "Local server"
      },
      {
        "url": "https://development.gigantic-server.com",
        "description": "Development server"
      },
      {
        "url": "https://staging.gigantic-server.com",
        "description": "Staging server"
      },
      {
        "url": "https://api.gigantic-server.com",
        "description": "Production server"
      }
    ],
  }
  

  
  interface_file_contents = [
    "export interface _BaseEntity {}",
    "\n\n\n"
  ]

  models_file_cotents = []
  model_relationships_file_cotents = []
  drizzle_file_cotents = [
    '''\
import { pgTable, serial, integer, text, boolean, timestamp, jsonb, varchar } from 'drizzle';
import { relations } from 'drizzle-orm';

    ''',
  ]
  drizzle_relationship_contents = []
  
  graphql_schema_file_cotents = []
  graphql_root_schema_fields = []
  
  contents: dict = {}

  with open("models.json", 'r') as f:
    contents = json.loads(f.read())
    
  relationships_definitions = contents.get("relationships", {})

  model_names = contents.get("models", {}).keys()

  if not model_names or len(model_names) == 0:
    print("No models found in config.")
    return
  
  global_model_names = model_names
  
  Path(f"{root_path}/graphql/schemas").mkdir(parents = True, exist_ok = True)

  
  
  for model_name in model_names:

    model_config = contents.get("models", {}).get(model_name, {})

    field_configs = model_config.get('fields', {})
    
    field_names = field_configs.keys()

    field_names_by_model[model_name] = field_names
    field_configs_by_model[model_name] = field_configs

    field_definitions_by_model[model_name] = [getFieldDef(field, field_configs[field]) for field in field_names]

  
  
  for model_name in model_names:

    model_config = contents.get("models", {}).get(model_name, {})
    field_configs = model_config.get('fields', {})

    kebob_name = camel_to_kebab(model_name)
    snake_name = camel_to_snake(model_name)
    
    model_name_plural = pluralize(model_name)
    
    kebob_name_plural = pluralize(kebob_name)

    model_var_name = model_name[0].lower() + model_name[1:]
    
    # --- #


    fields = field_configs_by_model[model_name]
    
    field_names = fields.keys()
    


    interface_contents = f'''\
export interface {model_name}Entity extends _BaseEntity {{
  {'\n  '.join(field_definitions_by_model[model_name])}
  <relationships>
}}
  '''
    
    model_object_contents = f'''\
export const {model_name} = sequelize.define({f'"{model_config['tableName']}"'}, { '{' }
  {'\n  '.join([ f"{field}: {{ type: DataTypes.{fields[field]['dataType'].upper()}, allowNull: {'false' if (fields[field]['required']) else 'true'}{', primaryKey: true, autoIncrement: true' if fields[field].get('primaryKey', False) else ''} }}," for field in field_names ])}
{ '});' if len(model_config.get('indexes', [])) == 0 else "}, " + f'''{{
  indexes: [
    {'\n    '.join([ f"{{ unique: {'true' if index.get('unique', False) else 'false'}, fields: [{ ', '.join([f'"{field}"' for field in index.get('fields', [])]) }] }}" for index in model_config.get('indexes', []) ])}
  ]
}});''' } 
  '''
    
    graphql_model_schema_cotents = f'''\
type {model_name} {{
  {'\n  '.join([ f"{field}: {'Int' if ('number' in field_definitions_by_model[model_name][index]) else 'String' if ('string' in field_definitions_by_model[model_name][index]) else 'Boolean'}" for index, field in enumerate(field_names) ])}
  <relationships>
}}
    '''

    graphql_root_schema_model_field = f'''{model_var_name}: Root{model_name}Query,'''
    graphql_root_schema_fields.append(graphql_root_schema_model_field)
    


    drizzle_model_contents = f'''\
export const {model_name_plural} = pgTable({f'"{model_config['tableName']}"'}, {{
  {'\n  '.join([ f"{field_name}: {getDrizzleDef(model_name, field_name)}" for index, field_name in enumerate(fields) ])}
}});
  '''

    graphql_model_object_contents = f'''\
import {{
  GraphQLFieldResolver,
  GraphQLResolveInfo,
  GraphQLObjectType,
  GraphQLString,
  GraphQLInt,
  GraphQLFieldConfig,
  GraphQLBoolean,
}} from 'graphql';
import {{ Container }} from "typedi";

export const Root{model_name}ByIdResolver: GraphQLFieldResolver<any, any> = (
  source: any,
  args: {{ id: number }},
  context: any,
  info: GraphQLResolveInfo
) => {{
  const {model_name}Repo: IModelCrud<{model_name}Entity> = Container.get({snake_name.upper()}_REPO_INJECT_TOKEN);
  return {model_name}Repo.findById(args.id);
}}

export const {model_name}Schema = new GraphQLObjectType({{
  name: '{model_name}',
  fields: {{
    {'\n    '.join([ f"{field}: {'{ type: GraphQLInt }' if ('number' in field_definitions_by_model[model_name][index]) else '{ type: GraphQLString }' if ('string' in field_definitions_by_model[model_name][index]) else '{ type: GraphQLBoolean }'}," for index, field in enumerate(fields) ])}
    <relationships>
  }},
}});

export const Root{model_name}Query: GraphQLFieldConfig<any, any> = {{
  type: {model_name}Schema,
  args: {{
    id: {{ type: GraphQLInt, description: `{model_name} Id` }}
  }},
  resolve: Root{model_name}ByIdResolver
}};
    '''



# }}, {{ indexes: [{{ unique: f{'true' if model_config.get('indexes', {}).get('unique', False) else 'false'}, fields: [{ ', '.join([]) }] }}] }});

    relationships = relationships_definitions.get(model_name, None)
    if not relationships:
      interface_contents = interface_contents.replace("\n  <relationships>", "")
      graphql_model_schema_cotents = graphql_model_schema_cotents.replace("\n  <relationships>", "")
      graphql_model_object_contents = graphql_model_object_contents.replace("\n    <relationships>", "")
    else:
      relationship_contents = []
      graphql_model_relationships_cotents = []
      graphql_object_relationships_cotents = []

      relationshipsHasOne = relationships.get("hasOne", {})
      relationshipsHasMany = relationships.get("hasMany", {})
      relationshipsBelongsTo = relationships.get("belongsToOne", {})
      relationshipsBelongsToMany = relationships.get("belongsToMany", {})

      for relation_model in relationshipsHasOne.keys():
        graphql_object_relationships_cotents.append(f'''{relationshipsHasOne[relation_model]['alias']}: {{
      type: {relation_model}Schema,
      resolve: (source: any, args: {{ {relationshipsHasOne[relation_model]['foreignKey']}: {getTypeScriptType(relation_model, relationshipsHasOne[relation_model]['foreignKey'])} }}, context: any, info: GraphQLResolveInfo) => {{
        const {relation_model}Repo: IModelCrud<{relation_model}Entity> = Container.get({camel_to_snake(relation_model).upper()}_REPO_INJECT_TOKEN);
        return {relation_model}Repo.findOne({{
          where: {{ {relationshipsHasOne[relation_model]['foreignKey']}: source.{relationshipsHasOne[relation_model]['sourceKey']} }}
        }});
      }},
    }},''')
        graphql_model_relationships_cotents.append(f'{relationshipsHasOne[relation_model]['alias']}({relationshipsHasOne[relation_model]['foreignKey']}: {getGraphqlSchemaType(relation_model, relationshipsHasOne[relation_model]['foreignKey'])}): {relation_model}')
        relationship_contents.append(f'{relationshipsHasOne[relation_model]['alias']}?: {relation_model}Entity;')
        drizzle_relationship_contents.append(f'''export const {model_name}To{relation_model}Relation = relations({pluralize(relation_model)}, ({{ one }}) => ({{
	{relationshipsHasOne[relation_model]['alias']}: one({pluralize(relation_model)}{ f''', {{
		fields: [{pluralize(relation_model)}.{relationshipsHasOne[relation_model]['foreignKey']}],
		references: [{model_name_plural}.{relationshipsHasOne[relation_model]['sourceKey']}],
	}})''' }
}}));''')
        model_relationships_file_cotents.append(f'{model_name}.hasOne({relation_model}, {{ as: "{relationshipsHasOne[relation_model]['alias']}", foreignKey: "{relationshipsHasOne[relation_model]['foreignKey']}", sourceKey: "{relationshipsHasOne[relation_model]['sourceKey']}" }});')
      
      for relation_model in relationshipsHasMany.keys():
        is_through_relation = relationshipsHasMany[relation_model].get('through', False)
        use_relation_model = relationshipsHasMany[relation_model]['through'] if is_through_relation else relation_model

        graphql_object_relationships_cotents.append(f'''{relationshipsHasMany[relation_model]['alias']}: {{
      type: {relation_model}Schema,
      resolve: (source: any, args: {{ {relationshipsHasMany[relation_model]['foreignKey']}: {getTypeScriptType(relation_model, relationshipsHasMany[relation_model]['foreignKey']) if not is_through_relation else getTypeScriptType(relationshipsHasMany[relation_model]['through'], relationshipsHasMany[relation_model]['foreignKey'])} }}, context: any, info: GraphQLResolveInfo) => {{
        const {relation_model}Repo: IModelCrud<{relation_model}Entity> = Container.get({camel_to_snake(relation_model).upper()}_REPO_INJECT_TOKEN);
        return {relation_model}Repo.findAll({{ {f'''
          include: [{{
            model: {relationshipsHasMany[relation_model]['through']},
            where: {{ {relationshipsHasMany[relation_model]['foreignKey']}: source.{relationshipsHasMany[relation_model]['sourceKey']} }}
          }}]''' 
          if is_through_relation else f'''
          where: {{ {relationshipsHasMany[relation_model]['foreignKey']}: source.{relationshipsHasMany[relation_model]['sourceKey']} }}\
          '''}
        }});
      }},
    }},''')
        graphql_model_relationships_cotents.append(f'{relationshipsHasMany[relation_model]['alias']}({relationshipsHasMany[relation_model]['foreignKey']}: {getGraphqlSchemaType(relation_model, relationshipsHasMany[relation_model]['foreignKey'])if not is_through_relation else getGraphqlSchemaType(relationshipsHasMany[relation_model]['through'], relationshipsHasMany[relation_model]['foreignKey'])}): [{relation_model}]')
        relationship_contents.append(f'{relationshipsHasMany[relation_model]['alias']}?: {relation_model}Entity[];')
        drizzle_relationship_contents.append(f'''export const {model_name}To{relation_model}Relations = relations({pluralize(relation_model)}, ({{ many }}) => ({{
	{relationshipsHasMany[relation_model]['alias']}: many({pluralize(relation_model)}{ f''', {{
		fields: [{pluralize(relation_model)}.{relationshipsHasMany[relation_model]['foreignKey']}],
		references: [{model_name_plural}.{relationshipsHasMany[relation_model]['sourceKey']}],
	}})''' }
}}));''')
        model_relationships_file_cotents.append(f'{model_name}.hasMany({relation_model}, {{ as: "{relationshipsHasMany[relation_model]['alias']}", foreignKey: "{relationshipsHasMany[relation_model]['foreignKey']}", sourceKey: "{relationshipsHasMany[relation_model]['sourceKey']}"{f', through: "{relationshipsHasMany[relation_model]['through']}"' if is_through_relation else ''} }});')
      
      for relation_model in relationshipsBelongsTo.keys():
        graphql_object_relationships_cotents.append(f'''{relationshipsBelongsTo[relation_model]['alias']}: {{
      type: {relation_model}Schema,
      resolve: (source: any, args: {{ {relationshipsBelongsTo[relation_model]['targetKey']}: {getTypeScriptType(relation_model, relationshipsBelongsTo[relation_model]['targetKey'])} }}, context: any, info: GraphQLResolveInfo) => {{
        const {relation_model}Repo: IModelCrud<{relation_model}Entity> = Container.get({camel_to_snake(relation_model).upper()}_REPO_INJECT_TOKEN);
        return {relation_model}Repo.findOne({{
          where: {{ {relationshipsBelongsTo[relation_model]['targetKey']}: source.{relationshipsBelongsTo[relation_model]['foreignKey']} }}
        }});
      }},
    }},''')
        graphql_model_relationships_cotents.append(f'{relationshipsBelongsTo[relation_model]['alias']}({relationshipsBelongsTo[relation_model]['foreignKey']}: {getGraphqlSchemaType(relation_model, relationshipsBelongsTo[relation_model]['targetKey'])}): {relation_model}')
        relationship_contents.append(f'{relationshipsBelongsTo[relation_model]['alias']}?: {relation_model}Entity;')
        drizzle_relationship_contents.append(f'''export const {model_name}To{relation_model}Relation = relations({pluralize(relation_model)}, ({{ one }}) => ({{
	{relationshipsBelongsTo[relation_model]['alias']}: one({pluralize(relation_model)}{ f''', {{
		fields: [{pluralize(relation_model)}.{relationshipsBelongsTo[relation_model]['targetKey']}],
		references: [{model_name_plural}.{relationshipsBelongsTo[relation_model]['foreignKey']}],
	}})''' }
}}));''')
        model_relationships_file_cotents.append(f'{model_name}.belongsTo({relation_model}, {{ as: "{relationshipsBelongsTo[relation_model]['alias']}", foreignKey: "{relationshipsBelongsTo[relation_model]['foreignKey']}", targetKey: "{relationshipsBelongsTo[relation_model]['targetKey']}" }});')
      
      for relation_model in relationshipsBelongsToMany.keys():
        is_through_relation = relationshipsBelongsToMany[relation_model].get('through', False)
        
        graphql_object_relationships_cotents.append(f'''{relationshipsBelongsToMany[relation_model]['alias']}: {{
      type: {relation_model}Schema,
      resolve: (source: any, args: {{ {relationshipsBelongsToMany[relation_model]['targetKey']}: {getTypeScriptType(relation_model, relationshipsBelongsToMany[relation_model]['targetKey']) if not is_through_relation else getTypeScriptType(relationshipsBelongsToMany[relation_model]['through'], relationshipsBelongsToMany[relation_model]['targetKey'])} }}, context: any, info: GraphQLResolveInfo) => {{
        const {relation_model}Repo: IModelCrud<{relation_model}Entity> = Container.get({camel_to_snake(relation_model).upper()}_REPO_INJECT_TOKEN);
        return {relation_model}Repo.findAll({{ {f'''
          include: [{{
            model: {relationshipsBelongsToMany[relation_model]['through']},
            where: {{ {relationshipsBelongsToMany[relation_model]['foreignKey']}: source.{relationshipsBelongsToMany[relation_model]['foreignKey']} }}
          }}]''' 
          if is_through_relation else f'''
          where: {{ {relationshipsBelongsToMany[relation_model]['targetKey']}: source.{relationshipsBelongsToMany[relation_model]['foreignKey']} }}\
          '''}
        }});
      }},
    }},''')
        graphql_model_relationships_cotents.append(f'{relationshipsBelongsToMany[relation_model]['alias']}({relationshipsBelongsToMany[relation_model]['foreignKey']}: {getGraphqlSchemaType(relation_model, relationshipsBelongsToMany[relation_model]['targetKey']) if not is_through_relation else getGraphqlSchemaType(relationshipsBelongsToMany[relation_model]['through'], relationshipsBelongsToMany[relation_model]['foreignKey'])}): [{relation_model}]')
        relationship_contents.append(f'{relationshipsBelongsToMany[relation_model]['alias']}?: {relation_model}Entity[];')
        drizzle_relationship_contents.append(f'''export const {model_name}To{relation_model}Relation = relations({pluralize(relation_model)}, ({{ one }}) => ({{
	{relationshipsBelongsToMany[relation_model]['alias']}: one({pluralize(relation_model)}{ f''', {{
		fields: [{pluralize(relation_model)}.{relationshipsBelongsToMany[relation_model]['targetKey']}],
		references: [{model_name_plural}.{relationshipsBelongsToMany[relation_model]['foreignKey']}],
	}})''' }
}}));''')
        model_relationships_file_cotents.append(f'{model_name}.belongsToMany({relation_model}, {{ as: "{relationshipsBelongsToMany[relation_model]['alias']}", foreignKey: "{relationshipsBelongsToMany[relation_model]['foreignKey']}", targetKey: "{relationshipsBelongsToMany[relation_model]['targetKey']}"{f', through: "{relationshipsBelongsToMany[relation_model]['through']}"' if is_through_relation else ''} }});')

      graphql_model_object_contents = graphql_model_object_contents.replace("<relationships>", "\n    " + "\n    ".join(graphql_object_relationships_cotents))
      graphql_model_schema_cotents = graphql_model_schema_cotents.replace("<relationships>", "\n  " + "\n  ".join(graphql_model_relationships_cotents))
      interface_contents = interface_contents.replace("<relationships>", "\n  " + "\n  ".join(relationship_contents))

    
    with open(f"{root_path}/graphql/schemas/{kebob_name_plural}.schema.ts", 'w') as f:
      f.write(graphql_model_object_contents)
      
    interface_file_contents.append(interface_contents)
    graphql_schema_file_cotents.append(graphql_model_schema_cotents)
    drizzle_file_cotents.append(drizzle_model_contents)

    models_file_cotents.append(model_object_contents)

    create_resource(model_name = model_name)

    model_openapi_specs = create_openapi_specs_from_model(model_name = model_name)

    my_merger.merge(openapi_specs, model_openapi_specs)

    

    has_user_owner_field: bool = False

    for field in field_names:
      field_config = fields[field]
      if field_config.get("references", {}).get("model", "") == "User":
        user_owner_field_by_model[model_name] = field
        has_user_owner_field = True
        break
    
    if has_user_owner_field:
      user_owner_field_by_model[model_name] = field

  joined_interface_contents = "\n\n".join(interface_file_contents)
  joined_graphql_schema_contents = "\n\n".join(graphql_schema_file_cotents)

  models_file_cotents.append('''\

/* --- Relationships --- */

''')
  models_file_cotents.extend(model_relationships_file_cotents)
  drizzle_file_cotents.append('''\

/* --- Relationships --- */

''')
  drizzle_file_cotents.extend(drizzle_relationship_contents)
  joined_model_object_contents = "\n\n".join(models_file_cotents)
  joined_drizzle_contents = "\n\n".join(drizzle_file_cotents)

  graphql_root_schema_contents = f'''\
export const rootGraphqlSchema = new GraphQLSchema({{

  query: new GraphQLObjectType({{
    name: 'RootQueryType',
    fields: {{
      {'\n      '.join([schema_field for schema_field in graphql_root_schema_fields])}
    }},
  }}),

}});
  '''

  with open(f"{root_path}/model-interfaces-converted.ts", 'w') as f:
    f.write(joined_interface_contents)

  with open(f"{root_path}/schema.graphql", 'w') as f:
    f.write(joined_graphql_schema_contents)

  with open(f"{root_path}/graphql/root.schema.ts", 'w') as f:
      f.write(graphql_root_schema_contents)

  with open(f"{root_path}/models.sequelize.ts", 'w') as f:
    f.write(joined_model_object_contents)

  with open(f"{root_path}/schema.drizzle.ts", 'w') as f:
    f.write(joined_drizzle_contents)


  model_types_contents = [
    'export enum ModelTypes {\n',
  ]
  for model_name in model_names:
    snake_name = camel_to_snake(model_name)
    model_types_contents.append(f'  {snake_name.upper()} = "{snake_name.upper()}",\n')
  model_types_contents.append('}\n')
    
  with open(f"{root_path}/model-types-converted.enum.ts", 'w') as f:
    f.write(''.join(model_types_contents))

  
  print(field_definitions_by_model)
    


  repository_service_contents = (f'''\
import 'reflect-metadata';
import {{ Service, Inject }} from "typedi";
import {{ IModelCrud }} from "../lib/utils/sequelize.utils";
import {{
  {'\n  '.join([ f"{model_name}Entity," for model_name in model_names ])}
}} from '@app/shared';
{'\n'.join([ f"import {{ {camel_to_snake(model_name).upper()}_REPO_INJECT_TOKEN }} from '../resources/{pluralize(camel_to_kebab(model_name))}/{pluralize(camel_to_kebab(model_name))}.repository';" for model_name in model_names ])}

                                 
@Service()
export class RepositoryService {{
                                 
  constructor(
    {'''\n    '''.join([ f"@Inject({camel_to_snake(model_name).upper()}_REPO_INJECT_TOKEN) public readonly {(model_name[0].lower() + model_name[1:])}Repo: IModelCrud<{model_name}Entity>," for model_name in model_names ])}
  ) {{}}
                                 
}}
        
''')
  
  regex_contents = ('''\
export const AUTH_BEARER_HEADER_REGEX: RegExp = /Bearer\s[^]/;
export const GENERIC_TEXT_REGEX: RegExp = /^[a-zA-Z0-9\s\'\-\_\.\@\$\#]{1,250}/;
export const PERSON_NAME_REGEX: RegExp = /^[a-zA-Z\s\'\-\_\.]{2,50}$/;
export const URL_REGEX = /[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)?/gi;
export const BASE64_REGEX = /^data:([A-Za-z-+\/]+);base64,(.+)$/;
export const MENTIONS_REGEX = /@[a-zA-Z0-9\-\_\.]{2,50}/gi;

export const YOUTUBE_URL_STANDARD = /http(s?):\/\/(www\.)?youtube\.com\/watch\?(.*)/gi;
export const YOUTUBE_URL_SHORT = /http(s?):\/\/(www\.)?youtu\.be\/(.*)/gi;
export const YOUTUBE_URL_EMBED = /http(s?):\/\/(www\.)?youtube\.com\/embed\/(.*)/gi;
export const YOUTUBE_URL_ID = /(v=[a-zA-Z0-9\-\_]{7,}|\/[a-zA-Z0-9\-\_]{7,})/gi;

export const LEADING_SPACES = /[\s]{2,}/;
export const LEADING_SPACES_GLOBAL = /[\s]{2,}/gi;

export const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
// export const PHONE_NUMBER_REGEX = /^\+?[1-9]\d{1,14}$/;
export const PHONE_NUMBER_REGEX = /^\+1\d{10}$/;
export const ZIP_CODE_REGEX = /^\d{5}$/;
export const IP_ADDRESS_REGEX = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/;
export const MAC_ADDRESS_REGEX = /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/;
export const UUID_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$/;
export const ISO_DATE_REGEX = /^\d{4}-\d{2}-\d{2}$/;
export const ISO_TIME_REGEX = /^\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?(?:Z|[+-]\d{2}:\d{2})?$/;
export const ISO_DATE_TIME_REGEX = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?(?:Z|[+-]\d{2}:\d{2})?$/;
export const ISO_OFFSET_REGEX = /^\d{2}:\d{2}$/;
export const COMMA_SEPARATED_LIST_REGEX = /^(\w+(?:\s*,\s*\w+)*)$/;
export const COMMA_SEPARATED_LIST_REGEX2 = /(([^,]+),?)/;
export const SEMICOLON_SEPARATED_LIST_REGEX = /^(\w+(?:\s*;\s*\w+)*)$/;

export const PERCENTAGE_REGEX = /^(\d{1,3}%)$/;
export const INTEGER_REGEX = /^(\d+)$/;
export const DECIMAL_REGEX = /^(\d+(?:\.\d*)?)$/;
export const TIME_REGEX = /^(\d{2}:\d{2}:\d{2})$/;
export const DATE_REGEX = /^(\d{4}-\d{2}-\d{2})$/;
export const DATETIME_REGEX = /^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})$/;
export const UUID_V4_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-4[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V5_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-5[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V6_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[6789AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V7_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-7[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V8_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-8[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V9_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-9[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V10_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-A[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V11_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-B[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;
export const UUID_V12_REGEX = /^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-C[0-9A-Fa-f]{3}-[89AB][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$/;

export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_REGEX = /^[a-zA-Z0-9\s\-\_]{1,250}$/;
export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_REGEX = /^[a-zA-Z0-9\s\-\_\.\@]{1,250}$/;
export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_REGEX = /^[a-zA-Z0-9\s\-\_\.\,]{1,250}$/;
export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_REGEX = /^[a-zA-Z0-9\s\-\_\.\,\:]{1,250}$/;
export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_REGEX = /^[a-zA-Z0-9\s\-\_\.\,\:\/]{1,250}$/;
export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_BRACKET_REGEX = /^[a-zA-Z0-9\s\-\_\.\,\:\/\[\]]{1,250}$/;
export const ALPHANUMERIC_SPACE_DASH_UNDERSCORE_DOT_COMMA_COLON_SLASH_BRACKET_PARENTHESIS_REGEX = /^[a-zA-Z0-9\s\-\_\.\,\:\/\[\]\(\)]{1,250}$/;

export const BOOLEAN_REGEX = /^(true|false)$/;

export const INTEGER_WITH_COMPARATOR_REGEX = /(^(eq|ne|gt|lt|gte|lte)<(\d+)>$|^(between|notBetween)<([\d]+,[\d]+)>$|^(in|notIn)<([\d]+(,[\d]+)*)>$)/;
// day of the week regex
export const DAY_OF_WEEK_REGEX = /^(mon|tue|wed|thu|fri|sat|sun)$/;
// full day of the week regex
// export const FULL_DAY_OF_WEEK_REGEX = /^(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$/;
export const DAYS_OF_THE_WEEK_REGEX = /^(?:sunday,?)?(?:monday,?)?(?:tuesday,?)?(?:wednesday,?)?(?:thursday,?)?(?:friday,?)?(?:saturday,?)?$/;
''')
  
  aws_s3_service = ('''\
import {
  S3Client,
  PutObjectCommand,
  CreateBucketCommand,
  GetObjectCommand,
  DeleteObjectCommand,
  DeleteBucketCommand,
  HeadBucketCommand,
  PutObjectCommandOutput
} from "@aws-sdk/client-s3";
import { v4 as uuidv4 } from 'uuid';
import { UploadedFile } from "express-fileupload";
import { readFileSync } from "fs";
import { HttpStatusCodes, MapType, ServiceMethodResults } from "@app/shared";
import { AppEnvironment, HttpRequestException, LOGGER } from "@app/backend";
import { isImageFileOrBase64, upload_base64, upload_expressfile } from "../lib/utils/request-file.utils";
import { IUploadFile } from "../lib/interfaces/common.interface";
import { readFile } from 'fs/promises';
import { Service } from "typedi";



// Create an Amazon S3 service client object.
// const s3Client = AppEnvironment.IS_ENV.LOCAL
//   ? new S3({
//     endpoint: 'http://localhost:4566',  // required for localstack
//     accessKeyId: 'test',
//     secretAccessKey: 'test',
//     s3ForcePathStyle: true,  // required for localstack
//   })
//   : new S3({ region: AppEnvironment.AWS.S3.REGION });

const s3Client = AppEnvironment.IS_ENV.LOCAL
  ? new S3Client({
      region: AppEnvironment.AWS.S3.REGION,
      forcePathStyle: true,
      endpoint: AppEnvironment.AWS.S3.ENDPOINT,
      credentials: {
        accessKeyId: 'test',
        secretAccessKey: 'test',
      }
    })
  : new S3Client({ region: AppEnvironment.AWS.S3.REGION })

export type AwsS3UploadResults = {
  Region: string,
  Bucket: string,
  Key: string,
  ContentType: string,
  Link: string,
  S3Url: string,
  Id: string,
};

export interface IAwsS3Service {
  createBucket(Bucket: string): Promise<any>;
  createObject(params: {
    Bucket: string,
    Key: string,
    Body: any,
    ContentType: string
  }): Promise<any>;
  getObject(params: {
    Bucket: string,
    Key: string
  }): Promise<any>;
  deleteBucket(Bucket: string): Promise<any>;
  deleteObject(params: {
    Bucket: string,
    Key: string
  }): Promise<any>;
  bucketExists(Bucket: string): Promise<boolean>;
}

// https://www.npmjs.com/package/s3-upload-stream


@Service()
export class AwsS3Service implements IAwsS3Service {

  isS3ConventionId(id: string) {
    return id.includes(`${AppEnvironment.AWS.S3.BUCKET}|`);
  }

  async uploadBuffer(
    buffer: Buffer,
    params: {
      filename: string,
      mimetype: string,
    }
  ) {
    try {
      if (!buffer || buffer.byteLength === 0) {
        throw new HttpRequestException(HttpStatusCodes.BAD_REQUEST, {
          message: `buffer is missing/empty`
        });
      }
  
      const Key = `public/static/uploads/${params.mimetype.toLowerCase()}/${uuidv4()}.${Date.now()}.${params.filename}`;
      const Id = `${AppEnvironment.AWS.S3.BUCKET}|${Key}`; // unique id ref for database storage; makes it easy to figure out the bucket and key for later usages/purposes.
      const Link = `${AppEnvironment.AWS.S3.SERVE_ORIGIN}/${Key}`;
      const S3Url = `${AppEnvironment.AWS.S3.S3_URL}/${AppEnvironment.AWS.S3.BUCKET}/${Key}`;
  
      await this.createObject({
        Body: buffer,
        Bucket: AppEnvironment.AWS.S3.BUCKET,
        Key,
        ContentType: params.mimetype.toLowerCase()
      });
  
      LOGGER.info(`Web link to new upload: ${Link}`);
  
      const results: AwsS3UploadResults = {
        Region: AppEnvironment.AWS.S3.REGION,
        Bucket: AppEnvironment.AWS.S3.BUCKET,
        Key,
        ContentType: params.mimetype.toLowerCase(),
        Link,
        S3Url,
        Id
      };
  
      LOGGER.info(`AWS S3 upload results:`, { results });
  
      return results;
    }
    catch (error) {
      console.error('s3 error', error);
      throw new HttpRequestException(HttpStatusCodes.INTERNAL_SERVER_ERROR, {
        message: `Could not upload to AWS S3; something went wrong`,
        context: error
      });
    }
  }

  async uploadFile(file: UploadedFile) {
    try {
      if (!file || file.size === 0) {
        throw new HttpRequestException(HttpStatusCodes.BAD_REQUEST, {
          message: `file is missing/empty`
        });
      }
  
      const buffer: Buffer = await readFile(file.tempFilePath);
  
      if (!buffer || buffer.byteLength === 0) {
        throw new HttpRequestException(HttpStatusCodes.BAD_REQUEST, {
          message: `file buffer is missing/empty`
        });
      }
  
      const Key = `public/static/uploads/${file.mimetype.toLowerCase()}/${uuidv4()}.${Date.now()}.${file.name}`;
      const Id = `${AppEnvironment.AWS.S3.BUCKET}|${Key}`; // unique id ref for database storage; makes it easy to figure out the bucket and key for later usages/purposes.
      const Link = `${AppEnvironment.AWS.S3.SERVE_ORIGIN}/${Key}`;
      const S3Url = `${AppEnvironment.AWS.S3.S3_URL}/${AppEnvironment.AWS.S3.BUCKET}/${Key}`;
  
      await this.createObject({
        Body: buffer,
        Bucket: AppEnvironment.AWS.S3.BUCKET,
        Key,
        ContentType: file.mimetype.toLowerCase()
      });
  
      LOGGER.info(`Web link to new upload: ${Link}`);
  
      const results: AwsS3UploadResults = {
        Region: AppEnvironment.AWS.S3.REGION,
        Bucket: AppEnvironment.AWS.S3.BUCKET,
        Key,
        ContentType: file.mimetype.toLowerCase(),
        Link,
        S3Url,
        Id
      };
  
      LOGGER.info(`AWS S3 upload results:`, { results });
  
      return results;
    }
    catch (error) {
      console.error('s3 error', error);
      throw new HttpRequestException(HttpStatusCodes.INTERNAL_SERVER_ERROR, {
        message: `Could not upload to AWS S3; something went wrong`,
        context: error
      });
    }
  }

  async uploadFileWithValidation(
    file: string | UploadedFile,
    options?: {
      treatNotFoundAsError: boolean,
      validateAsImage?: boolean,
      mutateObj?: MapType,
      id_prop?: string,
      link_prop?: string;
    }
  ) {
    if (!file) {
      const serviceMethodResults: ServiceMethodResults = {
        status: HttpStatusCodes.BAD_REQUEST,
        error: options && options.hasOwnProperty('treatNotFoundAsError') ? options?.treatNotFoundAsError : true,
        info: {
          message: `No argument found/given`
        }
      };
      
      const errMsg = `AwsS3Service.uploadFile - ${options?.treatNotFoundAsError ? 'error' : 'info'}: no file input...`;
      options?.treatNotFoundAsError
        ? LOGGER.error(errMsg, { options, serviceMethodResults })
        : LOGGER.info(errMsg, { options, serviceMethodResults });
      return serviceMethodResults;
    }

    if (!!options?.validateAsImage && !isImageFileOrBase64(file)) {
      const serviceMethodResults: ServiceMethodResults = {
        status: HttpStatusCodes.BAD_REQUEST,
        error: true,
        info: {
          message: `Bad file input given.`
        }
      };
      return serviceMethodResults;
    }

    try {
      let filepath: string = '';
      let filetype: string = '';
      let filename: string = '';
      let filedata: IUploadFile = null;
      
      if (typeof file === 'string') {
        // base64 string provided; attempt parsing...
        filedata = await upload_base64(file);
        filepath = filedata.file_path;
        filetype = filedata.filetype;
        filename = filedata.filename;
      }
      else {
        filedata = await upload_expressfile(file);
        filetype = (<UploadedFile> file).mimetype;
        filepath = filedata.file_path;
        filename = filedata.filename;
      }

      if (!filetype || !filename || !filepath) {
        throw new HttpRequestException(HttpStatusCodes.INTERNAL_SERVER_ERROR, {
          message: `file is missing data`,
          data: { filename, filepath, filetype, file }
        });
      }
  
      const Key = `public/static/uploads/${filetype.toLowerCase()}/${filename}`;
      const Id = `${AppEnvironment.AWS.S3.BUCKET}|${Key}`; // unique id ref for database storage; makes it easy to figure out the bucket and key for later usages/purposes.
      const Link = `${AppEnvironment.AWS.S3.SERVE_ORIGIN}/${Key}`;
      const S3Url = `${AppEnvironment.AWS.S3.S3_URL}/${AppEnvironment.AWS.S3.BUCKET}/${Key}`;

      const Body: Buffer = readFileSync(filepath);

      await this.createObject({
        Bucket: AppEnvironment.AWS.S3.BUCKET,
        Key,
        Body,
        ContentType: filetype.toLowerCase()
      });

      LOGGER.info(`Web link to new upload: ${Link}`);
  
      const results: AwsS3UploadResults = {
        Region: AppEnvironment.AWS.S3.REGION,
        Bucket: AppEnvironment.AWS.S3.BUCKET,
        Key,
        ContentType: filetype.toLowerCase(),
        Link,
        S3Url,
        Id
      };

      if (options && options.mutateObj && options.id_prop && options.link_prop) {
        options.mutateObj[options.id_prop] = Id;
        options.mutateObj[options.link_prop] = Link;
      }

      filedata?.remove();
  
      LOGGER.info(`AWS S3 upload results:`, { results });
      const serviceMethodResults: ServiceMethodResults<AwsS3UploadResults> = {
        status: HttpStatusCodes.OK,
        error: false,
        info: {
          data: results
        }
      };
      LOGGER.info(`AWS S3 upload results:`, { results });
      return serviceMethodResults;
    }
    catch (error) {
      const serviceMethodResults: ServiceMethodResults = {
        status: HttpStatusCodes.INTERNAL_SERVER_ERROR,
        error: true,
        info: {
          message: `Could not upload to AWS S3; something went wrong`
        }
      };
      LOGGER.error(serviceMethodResults.info.message || 'Error', { error });
      return serviceMethodResults;
    }
  }

  // create

  async createBucket(Bucket: string) {
    const data = await s3Client.send(new CreateBucketCommand({ Bucket }));
    console.log({ data, Bucket });
    LOGGER.info("Successfully created a bucket called:", { Bucket, data });
    return data; // For unit tests.
  }

  async createObject(params: {
    Bucket: string, // The name of the bucket. For example, 'sample_bucket_101'.
    Key: string, // The name of the object. For example, 'sample_upload.txt'.
    Body: any, // The content of the object. For example, 'Hello world!".
    ContentType: string
  }) {
    const results: PutObjectCommandOutput = await s3Client.send(new PutObjectCommand(params));
    delete params.Body;
    LOGGER.info(
      "Successfully created " +
      params.Key +
      " and uploaded it to " +
      params.Bucket +  "/" + params.Key +
      ", served as ",
      { results, params }
    );
    return results;
  }

  // get

  async getObject(params: {
    Bucket: string // The name of the bucket. For example, 'sample_bucket_101'.
    Key: string, // The name of the object. For example, 'sample_upload.txt'.
  }) {
    const results = await s3Client.send(new GetObjectCommand(params));
    LOGGER.info(
      "Successfully fetched " +
      params.Key +
      " and uploaded it to " +
      params.Bucket +
      "/" +
      params.Key,
      { results, params }
    );
    return results; // For unit tests.
  }

  // delete

  async deleteBucket(Bucket: string) {
    const data = await s3Client.send(new DeleteBucketCommand({ Bucket }));
    LOGGER.info(`Deleted Bucket ${Bucket}`, { data, Bucket });
    return data; // For unit tests.
  }

  async deleteObject(params: {
    Bucket: string, // The name of the bucket. For example, 'sample_bucket_101'.
    Key: string, // The name of the object. For example, 'sample_upload.txt'.
  }) {
    const results = await s3Client.send(new DeleteObjectCommand(params));
    LOGGER.info(
      "Successfully deleted " +
      params.Key +
      " from bucket " +
      params.Bucket,
      { results, params }
    );
    
    return results;
  }


  async bucketExists(Bucket: string): Promise<boolean> {
    try {
      const response = await s3Client.send(new HeadBucketCommand({ Bucket }));
      return true;
    }
    catch {
      return false;
    }
  }
}
''')
  

  
  with open(f"{root_path}/repository.service.ts", 'w') as f:
    f.write(''.join(repository_service_contents))

  with open(f"{root_path}/openapi.json", 'w') as f:
    f.write(json.dumps(openapi_specs, indent = 2))

  with open(f"{root_path}/common.regex.ts", 'w') as f:
    f.write(regex_contents)

  with open(f"{root_path}/s3.aws.ts", 'w') as f:
    f.write(aws_s3_service)




  controllers_list_contents = f'''\
{'\n'.join([ f"import {{ {model_name}Controller }} from './resources/{camel_to_kebab(model_name)}.controller.ts';" for model_name in global_model_names ])}

export const controllersList = [
  {'\n  '.join([ f"{model_name}Controller," for model_name in global_model_names ])}
];
  '''

  bootstrap_app_contents = f'''\
import 'reflect-metadata';
import fileUpload from 'express-fileupload';
import {{
  Application,
  json,
  static as staticRef,
}} from "express";
import {{ join as pathJoin }} from 'path';
import {{
  useExpressServer,
  useContainer as useContainerRoutingControllers,
  getMetadataArgsStorage
}} from 'routing-controllers';
import cookieParser from 'cookie-parser';
import {{ Container }} from 'typedi';
import {{ routingControllersToSpec }} from 'routing-controllers-openapi';
import {{ serve as SwaggerUiServe, setup as SwaggerUiSetup }} from 'swagger-ui-express';
import {{ readFileSync }} from "fs";
import {{ validationMetadatasToSchemas }} from 'class-validator-jsonschema'
import {{ firstValueFrom }} from "rxjs";



export async function bootstrapApp(app: Application) {{

  app.use('/static', staticRef(pathJoin(__dirname, 'assets', 'static')));

  const SwaggerUiMiddleware = SwaggerUiSetup(JSON.parse(readFileSync(pathJoin(__dirname, 'assets', 'static', 'openapi.json')).toString()));
  app.use('/api-docs', SwaggerUiServe, SwaggerUiMiddleware);
  app.use('/swagger', SwaggerUiServe, (request, response, next) => {{
    console.log(`Returning swagger ui`);
    const specs = JSON.parse(readFileSync(pathJoin(__dirname, 'assets', 'static', 'openapi.json')).toString());
    const middleware = SwaggerUiSetup(specs);
    middleware(request, response, next);
  }});

  const schemas = validationMetadatasToSchemas({{
    refPointerPrefix: '#/components/schemas/',
  }});
  const storage = getMetadataArgsStorage();
  const api_spec = routingControllersToSpec(storage, {{}}, {{
    components: {{ schemas: (schemas as any) }},
    info: {{ title: '', version: '1.0.0' }},
  }});

  const SwaggerUiMiddleware2 = SwaggerUiSetup(api_spec);
  app.use('/api-docs2', SwaggerUiServe, SwaggerUiMiddleware2);
  app.use('/swagger2', SwaggerUiServe, (request, response, next) => {{
    console.log(`Returning swagger ui`);
    const middleware = SwaggerUiSetup(api_spec);
    middleware(request, response, next);
  }});

  // health check
  app.get(['/health'], HealthCheckMiddleware);

  app.use(fileUpload({{
    preserveExtension: 100,
    uriDecodeFileNames: true,
    safeFileNames: true,
    useTempFiles: true,
    tempFileDir: pathJoin(__dirname, 'tmp'),
    debug: true,
    logger: {{
      log: (msg) => {{ LOGGER.info(msg); REQUESTS_FILE_LOGGER.info(msg) }}
    }},
    uploadTimeout: 60_000
  }}));

  app.use(cookieParser());

  app.use(json());

  app.use(ExpressJwtMiddleware);

  app.use(RequestLoggerMiddleware);

  await MountGraphqlExpress(app);

  initSocketIO(app);

  useExpressServer(app, {{
    controllers: controllersList,
    middlewares: [],
    defaultErrorHandler: false,
  }});

  
  // csrf token
  app.get(['/csrf'], GetCsrfTokenMiddleware);

  useContainerRoutingControllers(Container);
  
  // Http Request Exception
  app.use(HttpRequestExceptionExpressHandler);

}}

  '''

  expressjs_app_contents = '''\
/**
 * This is not a production server yet!
 * This is only a minimal backend to get started.
 */

import express from 'express';
import { bootstrapApp } from './app.init';

const app = express();

bootstrapApp(app).then(() => {
  const PORT = process.env['PORT'] || 3000;

  const server = app.listen(PORT, () => {
    console.log(`Listening at http://localhost:${PORT}`);
  });

  server.on('error', (error) => {
    console.error(error);
  });
});

  '''


  with open(f"{root_path}/app.controllers.ts", 'w') as f:
    f.write(''.join(controllers_list_contents))

  with open(f"{root_path}/app.init.ts", 'w') as f:
    f.write(bootstrap_app_contents)

  with open(f"{root_path}/app.ts", 'w') as f:
    f.write(expressjs_app_contents)




  with open(f"app/package.json", 'w') as f:
    f.write('''\
{
  "name": "@app/source",
  "version": "0.0.0",
  "license": "MIT",
  "scripts": {
    "nx": "nx",
    "remove-project": "nx generate @nx/workspace:remove",
    "tsc": "tsc",
    "webpack": "webpack"
  },
  "private": true,
  "devDependencies": {
    "@angular-devkit/build-angular": "~18.1.0",
    "@angular-devkit/core": "~18.1.0",
    "@angular-devkit/schematics": "~18.1.0",
    "@angular-eslint/eslint-plugin": "^18.0.1",
    "@angular-eslint/eslint-plugin-template": "^18.0.1",
    "@angular-eslint/template-parser": "^18.0.1",
    "@angular/cli": "~18.1.0",
    "@angular/compiler-cli": "~18.1.0",
    "@angular/language-service": "~18.1.0",
    "@expo/cli": "~0.18.13",
    "@nx/angular": "^19.5.7",
    "@nx/devkit": "19.5.7",
    "@nx/esbuild": "19.8.10",
    "@nx/eslint": "19.5.7",
    "@nx/eslint-plugin": "^19.5.7",
    "@nx/expo": "^19.5.7",
    "@nx/express": "^19.5.7",
    "@nx/jest": "19.8.10",
    "@nx/js": "19.8.10",
    "@nx/node": "19.8.10",
    "@nx/playwright": "19.5.7",
    "@nx/web": "19.5.7",
    "@nx/webpack": "19.5.7",
    "@nx/workspace": "19.5.7",
    "@playwright/test": "^1.36.0",
    "@pmmmwh/react-refresh-webpack-plugin": "^0.5.7",
    "@schematics/angular": "~18.1.0",
    "@svgr/webpack": "^8.0.1",
    "@swc-node/register": "~1.9.1",
    "@swc/core": "~1.5.7",
    "@swc/helpers": "~0.5.11",
    "@types/bcrypt-nodejs": "^0.0.31",
    "@types/cors": "^2.8.17",
    "@types/express": "^4.17.21",
    "@types/express-fileupload": "^1.5.0",
    "@types/helmet": "^4.0.0",
    "@types/jest": "^29.5.12",
    "@types/js-cookie": "^3.0.6",
    "@types/jsonwebtoken": "^9.0.6",
    "@types/lodash": "^4.17.7",
    "@types/moment": "^2.13.0",
    "@types/multer": "^1.4.11",
    "@types/node": "~18.16.9",
    "@types/node-fetch": "^2.6.11",
    "@types/sequelize": "^4.28.20",
    "@types/socket.io": "^3.0.2",
    "@types/swagger-ui-express": "^4.1.6",
    "@types/winston": "^2.4.4",
    "@types/yaml": "^1.9.7",
    "@typescript-eslint/eslint-plugin": "^7.16.0",
    "@typescript-eslint/parser": "^7.16.0",
    "@typescript-eslint/utils": "^7.16.0",
    "copy-webpack-plugin": "^12.0.2",
    "dotenv": "^16.4.5",
    "esbuild": "^0.19.2",
    "eslint": "~8.57.0",
    "eslint-config-prettier": "^9.0.0",
    "eslint-plugin-jsx-a11y": "^6.10.2",
    "eslint-plugin-playwright": "^0.15.3",
    "eslint-plugin-react": "^7.37.2",
    "jest": "^29.7.0",
    "jest-environment-jsdom": "^29.4.1",
    "jest-environment-node": "^29.7.0",
    "jest-preset-angular": "~14.1.0",
    "nodemon-webpack-plugin": "^4.8.2",
    "nx": "19.5.7",
    "prettier": "^2.8.8",
    "react-refresh": "^0.10.0",
    "routing-controllers": "^0.10.4",
    "tailwindcss": "^3.4.9",
    "ts-jest": "^29.1.0",
    "ts-loader": "^9.5.1",
    "ts-node": "10.9.1",
    "typescript": "~5.5.2",
    "webpack-cli": "^5.1.4",
    "webpack-node-externals": "^3.0.0"
  },
  "dependencies": {
    "@angular/animations": "~18.1.0",
    "@angular/common": "~18.1.0",
    "@angular/compiler": "~18.1.0",
    "@angular/core": "~18.1.0",
    "@angular/forms": "~18.1.0",
    "@angular/platform-browser": "~18.1.0",
    "@angular/platform-browser-dynamic": "~18.1.0",
    "@angular/router": "~18.1.0",
    "@aws-sdk/client-s3": "^3.629.0",
    "@aws-sdk/client-ses": "^3.629.0",
    "@gluestack-ui/nativewind-utils": "^1.0.23",
    "@gluestack-ui/overlay": "^0.1.15",
    "@gluestack-ui/toast": "^1.0.7",
    "@types/redis": "^4.0.10",
    "@vonage/server-sdk": "^3.19.2",
    "amqplib": "^0.10.4",
    "aws-sdk": "^2.1691.0",
    "axios": "^1.7.3",
    "bcrypt": "^5.1.1",
    "bcrypt-nodejs": "^0.0.3",
    "body-parser": "^1.20.2",
    "class-transformer": "^0.5.1",
    "class-transformer-validator": "^0.9.1",
    "class-validator": "^0.14.1",
    "class-validator-jsonschema": "^5.0.1",
    "cookie-parser": "^1.4.6",
    "cors": "^2.8.5",
    "eslint-plugin-react-hooks": "^5.0.0",
    "expo": "~51.0.8",
    "expo-server-sdk": "^3.10.0",
    "express": "^4.18.1",
    "express-csrf-protect": "^3.0.3",
    "express-device": "^0.4.2",
    "express-fileupload": "^1.5.1",
    "express-jwt": "^8.4.1",
    "form-data": "^4.0.0",
    "graphql": "^16.9.0",
    "graphql-http": "^1.22.1",
    "graphql-scalars": "^1.23.0",
    "handlebars": "^4.7.8",
    "helmet": "^7.1.0",
    "js-cookie": "^3.0.5",
    "jsonwebtoken": "^9.0.2",
    "lodash": "^4.17.21",
    "moment": "^2.30.1",
    "multer": "^1.4.5-lts.1",
    "nexmo": "^2.9.1",
    "node-fetch": "^3.3.2",
    "peer": "^1.0.2",
    "pg": "^8.12.0",
    "pg-hstore": "^2.3.4",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "react-native": "0.74.1",
    "react-native-svg": "^15.8.0",
    "redis": "^4.7.0",
    "reflect-metadata": "^0.2.2",
    "routing-controllers-openapi": "^4.0.0",
    "ruru": "^2.0.0-beta.13",
    "rxjs": "~7.8.0",
    "sequelize": "^6.37.3",
    "sequelize-typescript": "^2.1.6",
    "socket.io": "^4.8.0",
    "socket.io-stream": "^0.9.1",
    "stripe": "^16.7.0",
    "swagger-ui-express": "^5.0.1",
    "triple-beam": "^1.4.1",
    "tslib": "^2.3.0",
    "typedi": "^0.10.0",
    "uuid": "^10.0.0",
    "validator": "^13.12.0",
    "winston": "^3.14.1",
    "winston-daily-rotate-file": "^5.0.0",
    "yaml": "^2.5.0",
    "zone.js": "~0.14.3"
  }
}
''')
    
  with open(f"app/docker-compose.yml", 'w') as f:
    f.write('''
version: "3.8"

networks:
  # https://splunk.github.io/docker-splunk/EXAMPLES.html#create-standalone-and-universal-forwarder
  splunknet:
    driver: bridge
    attachable: true

volumes:

  # https://splunk.github.io/docker-splunk/STORAGE_OPTIONS.html
  # https://docs.docker.com/config/containers/logging/splunk/

  app-db-vol:
    driver: local

  file-server-vol:
    driver: local

  localstack-vol:
    driver: local

  localstack_pods:
    driver: local

  localstack-persistence-vol:
    driver: local

  opt-splunk-etc:
    driver: local

  opt-splunk-var:
    driver: local

  redis-cache-vol:
    driver: local

services:

  # uf1:
  #   networks:
  #     splunknet:
  #       aliases:
  #         - uf1
  #   image: ${UF_IMAGE:-splunk/universalforwarder:latest}
  #   hostname: uf1
  #   container_name: uf1
  #   environment:
  #     - SPLUNK_START_ARGS=--accept-license
  #     - SPLUNK_STANDALONE_URL=so1
  #     - SPLUNK_ADD=udp 1514,monitor /var/log/*
  #     - SPLUNK_PASSWORD=password
  #   ports:
  #     - 8089

  # so1:
  #   networks:
  #     splunknet:
  #       aliases:
  #         - so1
  #   image: ${SPLUNK_IMAGE:-splunk/splunk:latest}
  #   hostname: so1
  #   container_name: so1
  #   environment:
  #     - SPLUNK_START_ARGS=--accept-license
  #     - SPLUNK_STANDALONE_URL=so1
  #     - SPLUNK_PASSWORD=password
  #     - SPLUNK_LICENSE_URI=Free
  #   ports:
  #     - 8000
  #     - 8089
  #   volumes:
  #     - opt-splunk-etc:/opt/splunk/etc
  #     - opt-splunk-var:/opt/splunk/var

  # AWS mock - https://hub.docker.com/r/localstack/localstack
  # https://docs.localstack.cloud/user-guide/integrations/sdks/javascript/
  # aws-localstack:
  #   image: localstack/localstack
  #   ports:
  #     - "0.0.0.0:4566:4566"            # LocalStack Gateway
  #     - "0.0.0.0:4510-4559:4510-4559"  # external services port range
  #   environment:
  #     # LocalStack configuration: https://docs.localstack.cloud/references/configuration/
  #     DEBUG: ${DEBUG:-1}
  #     AWS_DEFAULT_REGION: us-east-1
  #   volumes:
  #     # - "localstack-vol:/var/lib/localstack"
  #     # - "/var/run/docker.sock:/var/run/docker.sock"

  #     - /var/run/docker.sock:/var/run/docker.sock
  #     - ./boot.sh:/etc/localstack/init/boot.d/boot.sh
  #     - ./ready.sh:/etc/localstack/init/ready.d/ready.sh
  #     - ./shutdown.sh:/etc/localstack/init/shutdown.d/shutdown.sh
  #     - localstack_pods:/pods

  # https://github.com/localstack/localstack/issues/6281
  # https://hub.docker.com/r/gresau/localstack-persist
  localstack-persistence:
    image: gresau/localstack-persist:3 # instead of localstack/localstack:3
    ports:
      - "4566:4566"
    volumes:
      - localstack-persistence-vol:/persisted-data

  # Databases

  app-db:
    image: postgres:latest
    restart: always
    environment:
      POSTGRES_PASSWORD: postgres_password
    ports:
      - '5431:5432'
    volumes: 
      - app-db-vol:/var/lib/postgresql/data

  # Cache

  redis-cache:
    image: redis:latest
    hostname: redis-cache
    environment:
      PASSWORD: password
    command: redis-server --requirepass password
    deploy:
      replicas: 1
    ports:
      - '6378:6379'
    volumes:
      - redis-cache-vol:/data


  # File-Server - https://hub.docker.com/r/flaviostutz/simple-file-server
  # simple-file-server:
  #   build: .
  #   image: flaviostutz/simple-file-server
  #   ports:
  #     - "4000:4000"
  #   environment:
  #     - WRITE_SHARED_KEY=
  #     - READ_SHARED_KEY=
  #     - LOCATION_BASE_URL=http://localhost:4000
  #     - LOG_LEVEL=debug
  #     - CHOKIDAR_USEPOLLING=true
  #   volumes:
  #     - file-server-vol:/data


  # Servers

  # app-server:
  #   build:
  #     context: .
  #     dockerfile: dockerfiles/expressjs.Dockerfile
  #     args:
  #       APP_NAME: app-server-expressjs
  #       SHARED_STORAGE_VOL_PATH: /app/shared-files
  #       LOGS_PATH: /app/logs
  #   command: npm run nx serve app-server
  #   deploy:
  #     replicas: 1
  #   env_file:
  #     - .env
  #   environment:
  #     APP_ENV: LOCAL
  #     APP_MACHINE_NAME: APP_SERVER_EXPRESSJS
  #     APP_DISPLAY_NAME: "App Server ExpressJS"
  #     LOGS_PATH: /app/logs
  #     COMPONENT: app-server-expressjs
  #     SHARED_STORAGE_VOL_PATH: /app/shared-files
  #     PORT: 4000
  #     JWT_SECRET: "0123456789"
  #     DATABASE_URL: postgres://postgres:postgres_password@app-db:5432
  #     CORS_WHITELIST_ORIGINS: http://localhost:4200,http://localhost:7600
  #     REDIS_URL: redis://default:password@redis-cache:6379

  #     PLATFORM_AWS_S3_REGION: us-east-1
  #     PLATFORM_AWS_S3_BUCKET: public-assets
  #     PLATFORM_AWS_S3_BUCKET_SERVE_ORIGIN: http://localhost:4566/public-assets
  #     PLATFORM_AWS_S3_ORIGIN: http://s3.us-east-1.localhost.localstack.cloud:4566
  #     PLATFORM_AWS_S3_ENDPOINT: http://localstack-persistence:4566

  #     SPLUNK_TOKEN: ""
  #     SPLUNK_HOST: so1

  #   depends_on:
  #     - app-db
  #     # - aws-localstack
  #     - localstack-persistence
  #   ports:
  #     - '4000:4000'
  #   volumes:
  #     - /app/node_modules
  #     - './src:/{root_path}'
  #     - './app-logs:/app/logs'

''')
  


def run():

  convert_models_to_resources()
  
  print("Finished!")
 
  
run()
