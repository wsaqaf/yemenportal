class ChangeReviewParentEntity < ActiveRecord::Migration[5.0]
  def change
    remove_reference :review_comments, :topic
    add_reference :review_comments, :post, foreign_key: { on_delete: :cascade }

    remove_reference :reviews, :topic
    add_reference :reviews, :post, foreign_key: { on_delete: :cascade }
  end
end
