class AddFieldsToSource < ActiveRecord::Migration[5.0]
  def change
    add_column :sources, :name, :string, null: false, default: ''
    add_column :sources, :website, :string
    add_column :sources, :brief_info, :string
    add_column :sources, :admin_email, :string
    add_column :sources, :admin_name, :string
    add_column :sources, :note, :string
  end
end
