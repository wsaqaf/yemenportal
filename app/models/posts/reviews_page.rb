class Posts::ReviewsPage
  attr_reader :post

  def initialize(user, post)
    @user = user
    @post = post
  end

  def flags
    all_flags.map do |flag|
      Flag.new(flag, reviews.find { |review| review.flag == flag }, user)
    end
  end

  def comments
    post.review_comments
  end

  def new_review_comment
    comments.new
  end

  private

  attr_reader :user

  def all_flags
    @_all_flags ||= ::Flag.all.include_number_of_reviews_for_post(post)
  end

  def reviews
    @_reviews ||= Review.where(moderator: user, post: post)
  end

  class Flag
    attr_reader :flag, :review, :user

    def initialize(flag, review, user)
      @flag = flag
      @review = review
      @user = user
    end

    delegate :id, :name, :color, :number_of_reviews_for_post, to: :flag

    def reviewed?
      review.present?
    end

    def read_only?
      !(policy.create? || policy.destroy?)
    end

    private

    def policy
      ReviewPolicy.new(user, review || Review.new)
    end
  end
end
