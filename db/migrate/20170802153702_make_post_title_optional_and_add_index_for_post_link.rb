class MakePostTitleOptionalAndAddIndexForPostLink < ActiveRecord::Migration[5.0]
  def change
    change_column(:posts, :title, :string, null: true)
    change_column(:posts, :published_at, :datetime, null: true)
    rename_column(:posts, :photo_url, :image_url) # not all images are photos
    add_index(:posts, :link)
  end
end
