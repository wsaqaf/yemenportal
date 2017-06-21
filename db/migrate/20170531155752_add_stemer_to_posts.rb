class AddStemerToPosts < ActiveRecord::Migration[5.0]
  def change
    add_column :posts, :stemmed_text, :text, default: ''
  end
end
