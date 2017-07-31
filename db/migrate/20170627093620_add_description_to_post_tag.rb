class AddDescriptionToPostTag < ActiveRecord::Migration[5.0]
  def change
    add_column :post_tags, :description, :string
  end
end
