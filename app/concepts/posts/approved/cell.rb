class Posts::Approved::Cell < Application::Cell
  include WillPaginate::ActionView

  private

  option :user_votes, :user, :topics
  property :title, :link, :published_at, :property

  def post_body
    concept("posts/approved/item/cell", collection: model, user_votes: user_votes, user: user)
  end

  def topic_body
    concept("topics/item/cell", collection: topics)
  end
end
