class AddTopicToPost < ActiveRecord::Migration[5.0]
  def up
    add_reference :posts, :topic, foreign_key: true
    remove_column :posts, :keywords
    drop_table :post_associations
  end

  def down
    remove_column :posts, :topic_id
    add_column :posts, :keywords, :string, array: true, default: []
    create_table :post_associations do |t|
      t.integer :main_post_id
      t.integer :dependent_post_id

      t.timestamps
    end
  end
end
