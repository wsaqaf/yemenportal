class Posts::Cell < Application::Cell
  include WillPaginate::ActionView

  private

  option :categories, :state, :votes, :user
  property :title, :link, :published_at, :property

  def posts_page
    concept("posts/#{state}/cell", model, categories: categories, user_votes: votes, user: user)
  end
end
