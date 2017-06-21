class Topics::Show::Cell < Application::Cell
  property :posts
  option :user_votes, :user

  private

  def post_body
    concept("posts/approved/item/cell", collection: posts, user_votes: user_votes, user: user)
  end

  def topic_header
    posts.ordered_by_date.last.title
  end
end
