class DropStopWordTable < ActiveRecord::Migration[5.0]
  def up
    drop_table :stop_words
  end

  def down
    create_table :stop_words do |t|
      t.string :name
      t.timestamps
    end
  end
end
