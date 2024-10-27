export const S3Object = sequelize.define("s3objects", {
  id: { type: DataTypes.INTEGER, allowNull: true, primaryKey: true, autoIncrement: true },
  metadata: { type: DataTypes.JSONB, allowNull: false },
  create_at: { type: DataTypes.DATETIME, allowNull: true },
  updated_at: { type: DataTypes.DATETIME, allowNull: false },
  deleted_at: { type: DataTypes.DATETIME, allowNull: false },
  model_type: { type: DataTypes.STRING, allowNull: false },
  model_id: { type: DataTypes.INTEGER, allowNull: false },
  mimetype: { type: DataTypes.STRING, allowNull: false },
  is_private: { type: DataTypes.BOOLEAN, allowNull: true },
  region: { type: DataTypes.STRING, allowNull: true },
  bucket: { type: DataTypes.STRING, allowNull: true },
  key: { type: DataTypes.STRING, allowNull: true },
});
  

export const User = sequelize.define("users", {
  id: { type: DataTypes.INTEGER, allowNull: true, primaryKey: true, autoIncrement: true },
  metadata: { type: DataTypes.JSONB, allowNull: false },
  create_at: { type: DataTypes.DATETIME, allowNull: true },
  updated_at: { type: DataTypes.DATETIME, allowNull: false },
  deleted_at: { type: DataTypes.DATETIME, allowNull: false },
  stripe_customer_account_id: { type: DataTypes.STRING, allowNull: false },
  stripe_account_id: { type: DataTypes.STRING, allowNull: false },
  stripe_account_verified: { type: DataTypes.BOOLEAN, allowNull: true },
  stripe_identity_verified: { type: DataTypes.BOOLEAN, allowNull: true },
  first_name: { type: DataTypes.STRING, allowNull: false },
  last_name: { type: DataTypes.STRING, allowNull: false },
  bio: { type: DataTypes.STRING, allowNull: false },
  icon_s3object_id: { type: DataTypes.INTEGER, allowNull: false },
  town: { type: DataTypes.STRING, allowNull: false },
  city: { type: DataTypes.STRING, allowNull: false },
  state: { type: DataTypes.STRING, allowNull: false },
  zipcode: { type: DataTypes.INTEGER, allowNull: false },
  country: { type: DataTypes.STRING, allowNull: false },
  tags: { type: DataTypes.TEXT, allowNull: false },
  specialties: { type: DataTypes.TEXT, allowNull: false },
  person_verified: { type: DataTypes.BOOLEAN, allowNull: true },
  email_verified: { type: DataTypes.BOOLEAN, allowNull: true },
  phone_verified: { type: DataTypes.BOOLEAN, allowNull: true },
});
  

export const UserAuthProvider = sequelize.define("user_auth_providers", {
  id: { type: DataTypes.INTEGER, allowNull: true, primaryKey: true, autoIncrement: true },
  metadata: { type: DataTypes.JSONB, allowNull: false },
  create_at: { type: DataTypes.DATETIME, allowNull: true },
  updated_at: { type: DataTypes.DATETIME, allowNull: false },
  deleted_at: { type: DataTypes.DATETIME, allowNull: false },
  details: { type: DataTypes.JSONB, allowNull: false },
  user_id: { type: DataTypes.INTEGER, allowNull: true },
  provider_name: { type: DataTypes.STRING, allowNull: true },
  provider_id: { type: DataTypes.STRING, allowNull: true },
});
  

export const Tag = sequelize.define("tags", {
  id: { type: DataTypes.INTEGER, allowNull: true, primaryKey: true, autoIncrement: true },
  metadata: { type: DataTypes.JSONB, allowNull: false },
  create_at: { type: DataTypes.DATETIME, allowNull: true },
  updated_at: { type: DataTypes.DATETIME, allowNull: false },
  deleted_at: { type: DataTypes.DATETIME, allowNull: false },
  name: { type: DataTypes.STRING, allowNull: true },
  description: { type: DataTypes.TEXT, allowNull: false },
});
  

export const UserTag = sequelize.define("user_tags", {
  id: { type: DataTypes.INTEGER, allowNull: true, primaryKey: true, autoIncrement: true },
  metadata: { type: DataTypes.JSONB, allowNull: false },
  create_at: { type: DataTypes.DATETIME, allowNull: true },
  updated_at: { type: DataTypes.DATETIME, allowNull: false },
  deleted_at: { type: DataTypes.DATETIME, allowNull: false },
  user_id: { type: DataTypes.INTEGER, allowNull: true },
  tag_id: { type: DataTypes.INTEGER, allowNull: true },
});
  

User.hasOne(S3Object, { as: "icon", foreignKey: "id", sourceKey: "icon_s3object_id" });

User.hasMany(UserAuthProvider, { as: "authProviders", foreignKey: "user_id", sourceKey: "id" });

UserAuthProvider.belongsTo(User, { as: "user", foreignKey: "user_id", targetKey: "id" });

UserTag.belongsTo(User, { as: "user", foreignKey: "user_id", targetKey: "id" });

UserTag.belongsTo(Tag, { as: "tag", foreignKey: "tag_id", targetKey: "id" });