class ChangeVoteParentEntityFromTopicToPost < ActiveRecord::Migration[5.0]
  class Vote < ApplicationRecord; end

  def change
    Vote.delete_all
    remove_reference :votes, :topic
    add_reference :votes, :post, foreign_key: { on_delete: :cascade }

    remove_column :topics, :voting_result, :integer, default: 0
    add_column :posts, :voting_result, :integer, default: 0
    add_index :posts, :voting_result
  end
end
