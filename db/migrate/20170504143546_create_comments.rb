class CreateComments < ActiveRecord::Migration[5.0]
  def change
    create_table :comments do |t|
      t.references :user, foreign_key: { on_delete: :cascade }
      t.text :body, null: false
      t.references :post, foreign_key: { on_delete: :cascade }

      t.timestamps
    end
  end
end
