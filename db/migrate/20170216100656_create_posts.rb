class CreatePosts < ActiveRecord::Migration[5.0]
  def change
    create_table :posts do |t|
      t.text :description
      t.datetime :pub_date, null: false
      t.string :link, null: false
      t.string :title, null: false

      t.timestamps
    end
  end
end
