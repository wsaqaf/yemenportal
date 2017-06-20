class CreatePostAssociations < ActiveRecord::Migration[5.0]
  def change
    create_table :post_associations do |t|
      t.integer :main_post_id
      t.integer :dependent_post_id

      t.timestamps
    end
  end
end
