class Topics::Item::Cell < Application::Cell
  include WillPaginate::ActionView
  SAME_POST_COUNT = 5

  private

  property :posts

  def main_post
    posts.ordered_by_date.last
  end

  def same_posts
    main_post.same_posts.last(SAME_POST_COUNT)
  end

  def description
    main_post.description
  end
end
