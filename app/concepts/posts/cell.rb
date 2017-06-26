class Posts::Cell < Application::Cell
  include WillPaginate::ActionView

  private

  option :state, :votes, :user, :topics
  property :title, :link, :published_at, :property

  def posts_page
    concept("posts/#{state}/cell", model, topics: topics, user_votes: votes, user: user)
  end
end
