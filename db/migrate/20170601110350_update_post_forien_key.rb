class UpdatePostForienKey < ActiveRecord::Migration[5.0]
  class Post < ActiveRecord::Base
  end

  def up
    posts = Post.all
    result_for_save = posts.map{|post| {id: post.id,  source_id: post.source_id}}
    remove_reference :posts, :source
    add_reference :posts, :source, foreign_key: { on_delete: :cascade }


    result_for_save.each do |data|
      post = posts.find{|post| post.id == data[:id]}
      post.update(source_id: data[:source_id])
    end
    Post.where(source_id: nil).delete_all

    change_column_null :posts, :source_id, false
  end

  def down
  end
end
