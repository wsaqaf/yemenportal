class MainPageController < ApplicationController
  MIN_TOPIC_SIZE = 2

  def show
    posts_list = posts.limit(15)
    render cell: true, model: posts_list, options: {
      categories: Category.all,
      state: :approved,
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
    Topic.includes(:posts).where("post_counts >= #{MIN_TOPIC_SIZE}").paginate(page: params[:page], per_page: 10)
  end

  def user_voted(posts)
    posts_ids = posts.map(&:id)
    current_user ? current_user.votes.votes_posts(posts_ids) : []
  end

  def category
    @_category = Category.find_by(name: params[:category])
  end
end
