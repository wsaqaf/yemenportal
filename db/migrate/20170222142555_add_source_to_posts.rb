class AddSourceToPosts < ActiveRecord::Migration[5.0]
  def change
    add_reference :posts, :source

    add_index :posts, :published_at
  end
end
