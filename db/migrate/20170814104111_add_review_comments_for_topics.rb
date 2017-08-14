class AddReviewCommentsForTopics < ActiveRecord::Migration[5.0]
  def change
    drop_table :comments
    create_table :review_comments do |t|
      t.belongs_to :author
      t.belongs_to :topic
      t.text :body
      t.timestamps
    end
  end
end
