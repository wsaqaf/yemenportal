class CreatePostTags < ActiveRecord::Migration[5.0]
  def change
    create_table :post_tags do |t|
      t.string :name
      t.references :user, foreign_key: { on_delete: :cascade }
      t.references :post, foreign_key: { on_delete: :cascade }

      t.timestamps
    end
  end
end
