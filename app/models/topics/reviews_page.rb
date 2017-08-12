class Topics::ReviewsPage
  attr_reader :topic

  def initialize(user, topic)
    @user = user
    @topic = topic
  end

  def flags
    all_flags.map do |flag|
      Flag.new(flag, reviews.find { |review| review.flag == flag }, user)
    end
  end

  private

  attr_reader :user

  def all_flags
    ::Flag.all.include_number_of_reviews_for_topic(topic)
  end

  def reviews
    @_reviews ||= Review.where(moderator: user, topic: topic)
  end

  class Flag
    attr_reader :flag, :review, :user

    def initialize(flag, review, user)
      @flag = flag
      @review = review
      @user = user
    end

    delegate :id, :name, :color, :number_of_reviews_for_topic, to: :flag

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
