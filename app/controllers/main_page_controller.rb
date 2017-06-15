class MainPageController < ApplicationController
  MIN_TOPIC_COUNT = 2

  def index
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
    @_posts ||= begin
      if category
        category.posts.includes(:votes).includes(:categories).approved_posts
      else
        Post.includes(:votes).includes(:categories).approved_posts
      end
    end
  end

  def topics
    ids = posts.where.not(topic_id: nil).pluck(:topic_id)
    Topic.includes(:posts).where(id: ids.detect { |id| ids.count(id) >= MIN_TOPIC_COUNT })
      .paginate(page: params[:page], per_page: 10)
  end

  def user_voted(posts)
    posts_ids = posts.map(&:id)
    if current_user
      current_user.votes.votes_posts(posts_ids)
    else
      []
    end
  end

  def category
    @_category = Category.find_by(name: params[:category])
  end
end
