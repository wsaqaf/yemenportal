class AddFlagsForTopics < ActiveRecord::Migration[5.0]
  def change
    create_table :flags do |t|
      t.string :name
      t.string :color
      t.boolean :resolve, default: false, null: false
    end

    create_table :reviews do |t|
      t.belongs_to :topic
      t.belongs_to :flag
      t.belongs_to :moderator
    end
  end
end
