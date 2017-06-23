class CreateStopWords < ActiveRecord::Migration[5.0]
  class StopWord < ApplicationRecord
  end

  def up
    create_table :stop_words do |t|
      t.string :name
      t.timestamps
    end

    stop_word = Rails.application.config_for(:stop_words)
    stop_word.each do |word|
      StopWord.find_or_create_by(name: word)
    end
  end


  def down
    drop_table :stop_words
  end
end
