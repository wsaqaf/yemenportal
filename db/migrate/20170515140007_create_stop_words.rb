class CreateStopWords < ActiveRecord::Migration[5.0]
  class StopWord < ApplicationRecord
  end

  def up
    create_table :stop_words do |t|
      t.string :name
      t.timestamps
    end
  end


  def down
    drop_table :stop_words
  end
end
