class AddPhotoToPost < ActiveRecord::Migration[5.0]
  def change
    add_column :posts, :photo_url, :string
  end
end
