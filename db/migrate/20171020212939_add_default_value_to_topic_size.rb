class AddDefaultValueToTopicSize < ActiveRecord::Migration[5.0]
  def up
    change_column_default :topics, :topic_size, 0
    Topic.where(topic_size: nil).update_all(topic_size: 0)
  end

  def down
    change_column_default :topics, :topic_size, nil
  end
end

