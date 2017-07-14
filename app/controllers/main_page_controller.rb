class MainPageController < ApplicationController
  MIN_TOPIC_SIZE = 2

  def show
    posts_list = posts.limit(15)
    render cell: true, model: posts_list, options: {
      votes: user_voted(posts_list),
      user: current_user,
      topics: topics
    }
  end

  private

  def posts
    @_posts ||= Post.includes(:votes).includes(:categories).approved_posts
  end

  def topics
    Topic.includes(:posts).where("topic_size >= ?", MIN_TOPIC_SIZE).paginate(page: params[:page], per_page: 10)
  end

  def user_voted(posts)
    posts_ids = posts.map(&:id)
    current_user ? current_user.votes.votes_posts(posts_ids) : []
  end
end
