class AddRolesToUsers < ActiveRecord::Migration[5.0]
  def up
    execute <<-SQL
      CREATE TYPE user_role AS ENUM ('ADMIN', 'MODERATOR', 'MEMBER');
    SQL

    add_column :users, :role, :user_role, index: true, null: false, default: 'MEMBER',
      comment: 'User role (Available: ADMIN, MODERATOR, MEMBER)'
  end

  def down
    remove_column :users, :role

    execute <<-SQL
      DROP TYPE user_role;
    SQL
  end
end
