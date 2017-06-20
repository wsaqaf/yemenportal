class AddKeyordsToPost < ActiveRecord::Migration[5.0]
  def change
    add_column :posts, :keywords, :string, array: true, default: []
  end
end
