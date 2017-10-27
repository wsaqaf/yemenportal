class Posts::Flagging
  def initialize(moderator:, post:, flag:)
    @moderator = moderator
    @post = post
    @flag = flag
  end

  def create_review
    if flag.resolve?
      delete_all_other_reviews
    else
      delete_review_with_resolve_flag
    end
    create_review_instance
  end

  private

  attr_reader :moderator, :post, :flag

  def delete_all_other_reviews
    Review.transaction do
      rate_applier.subtract_rate(other_reviews.reviews_rate)
      other_reviews.destroy_all
    end
  end

  def delete_review_with_resolve_flag
    Review.transaction do
      rate_applier.subtract_rate(resolving_reviews.reviews_rate)
      resolving_reviews.destroy_all
    end
  end

  def create_review_instance
    Post.transaction do
      Review.create(moderator: moderator, post: post, flag: flag)
      rate_applier.add_rate(flag.rate)
    end
  end

  def rate_applier
    @_rate_applier ||= Posts::Flagging::RateApplier.new(post)
  end

  def resolving_reviews
    @_resolving_reviews ||= Review.with_resolve_flag(post, moderator)
  end

  def other_reviews
    @_other_reviews ||= Review.where(post: post, moderator: moderator)
  end
end
